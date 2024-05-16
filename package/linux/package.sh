#!/bin/sh

cd ./../../
pyinstaller linux.spec --noconfirm
cd package/linux
rm -r data/usr/local/bin/*
cp -r ./../../dist/arma-s3.5 data/usr/local/bin/
fpm -C data -s dir -t deb --after-install control/postinst --after-remove control/prerem -n "arma-s35" -v 1.0.12 -m ARMA --url " " --description 'ARMA S3.5 manager' -p arma-s3.5.deb -f