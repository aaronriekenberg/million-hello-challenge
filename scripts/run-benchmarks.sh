#!/bin/bash

set -e

echo "begin run-benchmarks.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

export OUTPUT_FILE=results/raw.md
echo "OUTPUT_FILE=$OUTPUT_FILE"


# run nginx benchmarks
export SERVER_COMMAND="nginx -e stderr -p $REPO_ROOT/nginx-server/ -c $REPO_ROOT/nginx-server/nginx.conf"
export TEST_NAME=nginx
$SCRIPT_DIR/run-server-benchmark.sh


# build rust
echo "rustup update"
rustup update
cd rust-server
echo "$(date) before cargo build"
cargo build --release
echo "$(date) after cargo build"
cd -
echo "pwd = $(pwd)"

# run rust benchmarks
export SERVER_COMMAND='./rust-server/target/release/rust-server'
export TEST_NAME=rust
$SCRIPT_DIR/run-server-benchmark.sh


# build go
cd go-server
echo "$(date) before go build"
go build
echo "$(date) after go build"
cd -
echo "pwd = $(pwd)"

# run go benchmarks
export SERVER_COMMAND='./go-server/go-server'
export TEST_NAME=go
$SCRIPT_DIR/run-server-benchmark.sh


# build kotlin
echo "java --version"
java --version

cd kotlin-server
echo "$(date) before kotlin-server gradle build"

./gradlew clean build
cd build/distributions
tar xvf kotlin-server.tar
cd ../../..

echo "killall java"
killall java

echo "$(date) after gradle build"
echo "pwd = $(pwd)"

# run kotlin benchmarks
export SERVER_COMMAND='./kotlin-server/build/distributions/kotlin-server/bin/kotlin-server'
export TEST_NAME=kotlin
$SCRIPT_DIR/run-server-benchmark.sh


# node server
echo "node --version"
node --version

# run node benchmarks
export SERVER_COMMAND='node node-server/server.mjs'
export TEST_NAME=node
$SCRIPT_DIR/run-server-benchmark.sh


# python server
echo "python --version"
python --version

# python install tornado
echo "pip install tornado"
pip install tornado

# run python benchmarks
export SERVER_COMMAND='python python-server/server.py'
export TEST_NAME=python
$SCRIPT_DIR/run-server-benchmark.sh

echo "end run-benchmarks.sh"
