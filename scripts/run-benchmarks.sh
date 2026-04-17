#!/bin/bash

set -e

echo "begin run-benchmarks.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

export OUTPUT_FILE=results/raw.md
echo "OUTPUT_FILE=$OUTPUT_FILE"


# run nginx benchmarks
export API_COMMAND="nginx -e stderr -p $REPO_ROOT/nginx-api/ -c $REPO_ROOT/nginx-api/nginx.conf"
export TEST_NAME=nginx
$SCRIPT_DIR/run-api-benchmark.sh


# build rust
echo "rustup update"
rustup update
cd rust-api
echo "$(date) before cargo build"
cargo build --release
echo "$(date) after cargo build"
cd -
echo "pwd = $(pwd)"

# run rust benchmarks
export API_COMMAND='./rust-api/target/release/rust-api'
export TEST_NAME=rust
$SCRIPT_DIR/run-api-benchmark.sh


# build go
cd go-api
echo "$(date) before go build"
go build
echo "$(date) after go build"
cd -
echo "pwd = $(pwd)"

# run go benchmarks
export API_COMMAND='./go-api/go-api'
export TEST_NAME=go
$SCRIPT_DIR/run-api-benchmark.sh


# build kotlin
echo "java --version"
java --version

cd kotlin-api
echo "$(date) before kotlin-api gradle build"

./gradlew clean build
cd build/distributions
tar xvf kotlin-api.tar
cd ../../..

echo "killall java"
killall java

echo "$(date) after gradle build"
echo "pwd = $(pwd)"

# run kotlin benchmarks
export API_COMMAND='./kotlin-api/build/distributions/kotlin-api/bin/kotlin-api'
export TEST_NAME=kotlin
$SCRIPT_DIR/run-api-benchmark.sh


# node api
echo "node --version"
node --version

# run node benchmarks
export API_COMMAND='node node-api/server.mjs'
export TEST_NAME=node
$SCRIPT_DIR/run-api-benchmark.sh


# python api
echo "python --version"
python --version

# python install tornado
echo "pip install tornado"
pip install tornado

# run python benchmarks
export API_COMMAND='python python-api/server.py'
export TEST_NAME=python
$SCRIPT_DIR/run-api-benchmark.sh

echo "end run-benchmarks.sh"
