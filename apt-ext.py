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
from setproctitle import setproctitle


class OldKernelFilter(Filter):
    def apply(self, package):
        installed = package.is_installed
        starts_with_linux = package.shortname.startswith("linux")

        ends_with_section = False

        for section in frozenset({"backports-modules", "restricted-modules", "headers", "image", "tools"}):
            if section in package.shortname:
                ends_with_section = True

        correct_version = False

        current_linux_version = release().split("-")
        current_linux_version = current_linux_version[0] + "-" + current_linux_version[1]

        for character in package.shortname:
            if character.isdigit():
                correct_version = current_linux_version not in package.shortname

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


def all_files(exclude = {"/home", "/dev", "/media", "/mnt",
                         "/opt", "/proc", "/root", "/run",
                         "/sys", "/tmp", "/var"}) -> list:
    """
    Returns the absolute paths of all files in /,
    including subdirectories.
    @param exclude: Directories that won't be searched.
    """
    folders = list(set(glob("/*")) - exclude)
    result = []

    for folder in folders:
        for root, dirnames, filenames in walk(folder):
            for dirname in dirnames:
                result.append(join(root, dirname))
            for filename in filenames:
                result.append(join(root, filename))
    return result


def generate(text: list) -> str:
    return str.strip("".join(text))


if __name__ == "__main__":
    setproctitle("apt-ext")

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

            file = pipeline.open(argv[2], "w")
            file.write("")
            file.close()

            exit()

        elif argv[1] == "restore":
            command = ["apt", "install"]

            with open(argv[2], "r") as file:
                for line in file.readlines():
                    command.append(line.replace("\n", ""))

            call(command)
            exit()

        else:
            raise SyntaxError

    except KeyboardInterrupt:
        exit("\n Program exited.")
    except IOError as error:
        exit("{0}: {1}".format(error.strerror, error.filename))
    except (SyntaxError, IndexError):
        exit("Usage: {0} oldkernels|unmanaged|missing|backup [file]|restore [file]".format(basename(argv[0])))
