FROM fedora:38

RUN dnf install -y bzip2 ccache chrpath cpio cpp diffstat diffutils file \
findutils gawk gcc gcc-c++ git glibc-devel glibc-langpack-en gzip hostname \
libacl lz4 make patch perl perl-Data-Dumper perl-File-Compare perl-File-Copy \
perl-FindBin perl-Text-ParseWords perl-Thread-Queue perl-bignum perl-locale \
python python3 python3-GitPython python3-jinja2 python3-pexpect python3-pip \
rpcgen socat tar texinfo unzip wget which xz zstd \
python3-virtualenv python3-pip python3-setuptools virtualenv rsync

RUN useradd oebuilds
USER oebuilds

WORKDIR /home/oebuilds

RUN <<EOF
virtualenv -p python3 labgrid-venv
source labgrid-venv/bin/activate
pip install --upgrade pip
pip install labgrid
EOF

RUN <<EOF
mkdir .ssh
EOF

COPY --chmod=600 --chown=oebuilds:oebuilds sshconfig .ssh/config
COPY --chmod=600 --chown=oebuilds:oebuilds sshknown_hosts .ssh/known_hosts

CMD ["/bin/bash"]

