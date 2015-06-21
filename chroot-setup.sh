#!/bin/bash
set -x
CHROOT=/pool/jail

cd $CHROOT

#cp -r /root root
#mkdir -p {bin,dev,etc,lib,lib64,opt,proc,root,run,sbin,tmp,usr,var}

mount --bind /usr/ usr/ -o ro
mount --bind /bin bin -o ro
mount --bind /dev dev -o ro
mount --bind /proc proc -o ro
mount --bind /lib lib -o ro
mount --bind /lib64/ lib64 -o ro
mount --bind /etc/ etc -o ro
mount --bind /opt opt -o ro
mount --bind /sbin sbin/ -o ro
mount --bind /var var -o ro
mount --bind /root root -o ro

echo "Run: chroot $CHROOT"
#chroot $CHROOT $1

