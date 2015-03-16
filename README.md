# apt-ext

A package manager is a great tool. It enhances your system security by downloading every software package from a central, safe repository and by updating all your software automatically. Of course you can completely remove any package without leaving traces like dead links or anything like that. I really love this stress-free approach of software management.

One of these package managers is APT, the Advanced Packaging Tool, used by Ubuntu and Debian. APT can be extended with scripts and that's exactly what I did to automate some tasks I often need to do. I'm publishing these extensions here in the hope that they will be useful to somebody else. If I write more extensions, I will add them here.

All extensions are part of one single script called `apt-ext.py`. To use it, copy the script to a directory included in your $PATH, like ~/.local/bin (you can remove the .py file extension).

## Extensions

### oldkernels

APT can update your kernel automatically, but usually it does not override your old one. Instead, each kernel version comes in a separate package which can be installed in parallel. This way you can still switch back to your old kernel version even if the new one isn't working (usually you can select the kernel version in your bootloader's menu).

But in most cases the new kernel is working great, so you you don't need to keep all the old kernels versions you got from all the kernels updates. They are wasting space, which is especially valuable on a small and expensive SSD.

The extension prints out a list of all packages containing a kernel (except the currently running kernel). This includes the `linux-image`-packages, but also `linux-headers` and `linux-tools`.

To remove the old kernels packages, simply pass the list to `apt`:

    $ sudo apt purge $(apt-ext oldkernels)

### unmanged

Not all applications can be installed using the package manager. In some cases, there are no packages for the application, or you want to build from source code. The package manager does not know about these applications, so if you want to remove them, you have to do this by hand. Additionally, some applications generate caches or logfiles which are also not known by the package manager and have to be removed manually.

You can find those files using the `unmanaged` extension. It creates a list of the absolute paths of all files that are on your computer but not registered in the database. On my machine, the creation of this list took about four seconds with 500.000 files searched. The list is written to the standard output.

    $ apt-ext unmanaged > unmanaged.txt

### missing

This extensions does the opposite of `unmanaged`. It prints out a list with the absolute paths of all files that are registered with APT, but not on your computer - maybe because you deleted them by accident. The list can be useful when you want to repair an application because you just need to reinstall the packages containing the missing files.

You can use it just like that:

    $ apt-ext missing > missing.txt

### backup and restore

I use these ones for my regular backup. `backup` creates a list of all packages currently installed. `restore` can read this list and install the packages again on a fresh system.

Examples:

    $ apt-ext backup > apt.txt

Writes your package list to apt.txt.

    $ apt-ext restore < apt.txt

Installs all packages listed in apt.txt.

## Dependencies

`python3`, `python3-apt`, `awk`
