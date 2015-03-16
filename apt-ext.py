#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 David Haller <davidhaller@outlook.com>
#
# apt-ext is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# apt-ext is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from glob import glob
from os import walk
from os.path import basename, isdir, join
from pipes import Template
from platform import release
from subprocess import call
from sys import argv, exit

from apt.cache import Cache, Filter, FilteredCache


class OldKernelFilter(Filter):
    def apply(self, package):
        installed = package.is_installed

        """
        Checks if packages belongs to one of the kernel package types.
        """

        starts_with_linux = package.shortname.startswith("linux")
        ends_with_section = False

        for section in frozenset({"backports-modules", "restricted-modules", "headers", "image", "tools"}):
            if section in package.shortname:
                ends_with_section = True
                break

        """
        Checks if package is not a metapackage (contains a version string)
        and that the package does not contain the currently running kernel.
        """

        current_version = release().split("-")
        current_version = current_version[0] + "-" + current_version[1]
        correct_version = current_version not in package.shortname and "." in package.shortname

        return installed and starts_with_linux and ends_with_section and correct_version


def managed_files() -> list:
    """
    Returns a list with the absolute paths
    of all installed files.
    """
    cache = Cache()
    result = []

    for package in cache:
        if package.is_installed:
            result += package.installed_files

    return result


def all_files(exclude={"/home", "/dev", "/media", "/mnt",
                       "/opt", "/proc", "/root", "/run",
                       "/sys", "/tmp", "/var"}) -> list:
    """
    Returns the absolute paths of all files in /,
    including subdirectories.
    @param exclude: Directories that won't be searched.
    """
    folders = set(glob("/*")) - exclude
    result = []

    for folder in folders:
        for root, dirnames, filenames in walk(folder):
            for dirname in dirnames:
                result.append(join(root, dirname))
            for filename in filenames:
                result.append(join(root, filename))
    return result


def generate(text: list) -> str:
    return str.strip(str().join(text))


if __name__ == "__main__":
    try:
        if argv[1] == "oldkernels":
            cache = FilteredCache()
            cache.set_filter(OldKernelFilter())
            output = []

            for package in cache:
                output.append(package.shortname)
                output.append(" ")

            print(generate(output))
            exit()

        elif argv[1] == "unmanaged":
            result = sorted(set(all_files()) - set(managed_files()))
            output = []

            for path in result:
                output.append(path)
                output.append("\n")

            print(generate(output))
            exit()

        elif argv[1] == "missing":
            result = sorted(set(managed_files()) - set(all_files()))
            output = []

            for path in result:
                if not isdir(path):
                    output.append(path)
                    output.append("\n")

            print(generate(output))
            exit()

        elif argv[1] == "backup":
            pipeline = Template()
            pipeline.append("dpkg --get-selections", "--")
            pipeline.append("awk '{print $1}'", "--")

            with pipeline.open("/dev/stdout", "w") as packages:
                packages.write("")

            exit()

        elif argv[1] == "restore":
            command = ["sudo", "apt", "install"]

            with open("/dev/stdin", "r") as packages:
                for package in packages.readlines():
                    command.append(package.replace("\n", ""))

            call(command)
            exit()
        else:
            raise SyntaxError

    except KeyboardInterrupt:
        exit("\nProgram aborted by user.")
    except IOError as error:
        exit("{0}: {1}".format(error.strerror, error.filename))
    except (SyntaxError, IndexError):
        exit("Usage: {0} oldkernels|unmanaged|missing|backup|restore".format(basename(argv[0])))
