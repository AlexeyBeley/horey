#!/bin/bash
set -ex


mkdir -p "/opt/chrome"
unzip -q $download_path_chrome_linux -d "/opt/chrome"
rm -rf $download_path_chrome_linux

mkdir -p "/opt/chrome-driver"
unzip -q $dowload_path_chrome_driver_linux -d "/opt/chrome-driver"
rm -rf $dowload_path_chrome_driver_linux
