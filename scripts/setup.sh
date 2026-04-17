#!/bin/bash

set -e
set -o pipefail

echo "begin setup.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "installing latest stable nginx from nginx.org"
sudo apt-get update
sudo apt-get install -y curl gpg lsb-release ca-certificates ubuntu-keyring
curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor \
  | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] \
https://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" \
  | sudo tee /etc/apt/sources.list.d/nginx.list >/dev/null
echo -e "Package: *\nPin: origin nginx.org\nPin-Priority: 900\n" \
  | sudo tee /etc/apt/preferences.d/99nginx >/dev/null
sudo apt-get update
sudo apt-get install -y nginx
echo "verify nginx package source is nginx.org"
apt-cache policy nginx | tee /tmp/nginx-policy.txt
grep -q "nginx.org/packages/ubuntu" /tmp/nginx-policy.txt
echo "nginx version:"
nginx -v

echo "wget https://github.com/hatoo/oha/releases/latest/download/oha-linux-amd64"
wget https://github.com/hatoo/oha/releases/latest/download/oha-linux-amd64
mv oha-linux-amd64 oha
chmod +x ./oha

echo "oha --version"
./oha --version

OUTPUT_FILE=results/raw.md
echo "OUTPUT_FILE=$OUTPUT_FILE"

rm -f $OUTPUT_FILE
echo '# Results' >> $OUTPUT_FILE

echo '## Timestamp' >> $OUTPUT_FILE
date | xargs echo >> $OUTPUT_FILE

echo '## Hardware Info' >> $OUTPUT_FILE
echo '| CPU Model | Num CPUs | Memory |' >> $OUTPUT_FILE
echo '| --------- | -------- | ------ |' >> $OUTPUT_FILE

CPU_MODEL=$(lscpu  | grep 'Model name' | cut -f2 -d ':' | xargs)
echo "CPU_MODEL=$CPU_MODEL"

NUM_CPUS=$(lscpu | grep 'CPU(s):' | grep -v NUMA  | cut -f2 -d ':' | xargs)
echo "NUM_CPUS=$NUM_CPUS"

TOTAL_MEMORY=$(lsmem  |grep 'Total online' | cut -f2 -d':' | xargs)
echo "TOTAL_MEMORY=$TOTAL_MEMORY"

echo "| $CPU_MODEL | $NUM_CPUS | $TOTAL_MEMORY |" >> $OUTPUT_FILE
echo >> $OUTPUT_FILE

echo '## Benchmarks of 1 Million Requests' >> $OUTPUT_FILE
echo '| Test Name | HTTP Conns | Success Rate | Test Seconds | Requests per Second | P50 Millis | P99 Millis | P99.9 Millis | API Memory MB | API CPU Time | API Threads | API Processes |' >> $OUTPUT_FILE
echo '| --------- | ---------- | ------------ | ------------ | ------------------- | ---------- | ---------- | ------------ | ------------- | ------------ | ----------- | ------------- |' >> $OUTPUT_FILE

echo "created md header OUTPUT_FILE=$OUTPUT_FILE"
cat $OUTPUT_FILE
