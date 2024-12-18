Building Xilinx based systems with meta-xilinx
=============================================
This repository provides git submodules to setup the OpenEmbedded build system
with meta-xilinx to build images for Xilnx development boards and some vendor
boards.

OpenEmbedded allows the creation of custom linux distributions for embedded
systems. It is a collection of git repositories known as *layers* each of
which provides *recipes* to build software packages as well as configuration
information.

Information about the branch names is available at
https://wiki.yoctoproject.org/wiki/Releases.

Getting Started
---------------

1. Clone the git repository:

    $ git clone https://github.com/balister/xilinx-minimal.git

2. Check out the appropriate branch (default is OK for now):

    $ cd xilinx-minimal

3. Update the submodules (meta-xilinx also has a submodule):

    $ git submodule update --init --recursive

4. Initialize the build system:

    $ TEMPLATECONF=\`pwd\`/meta-xilinx-minimal/conf/templates/default  source ./openembedded-core/oe-init-build-env ./build ./bitbake

5. Select the MACHINE to build for:

    $ export MACHINE=zcu102-zynqmp   (default from local.conf)

6. Build an image:

    $ bitbake core-image-minimal

8. Build an sdk:

    $ bitbake -c populate_sdk core-image-minimal


