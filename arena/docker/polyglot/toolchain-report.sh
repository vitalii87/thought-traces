#!/bin/sh
set -eu

python3 --version
gcc --version | head -n 1
g++ --version | head -n 1
clang --version | head -n 1
rustc --version
cargo --version
go version
fpc -iV
javac -version
