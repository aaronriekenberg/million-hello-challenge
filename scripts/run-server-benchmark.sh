#!/bin/bash

set -e

echo "begin run-server-benchmark.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

lscpu
lsmem

for NUM_CONNECTIONS in 200 400 800; do

    echo "NUM_CONNECTIONS=$NUM_CONNECTIONS"

    echo "runnning SERVER_COMMAND = $SERVER_COMMAND"

    $SERVER_COMMAND &
    SERVER_PID=$!

    sleep 1

    echo "$TEST_NAME running PID $SERVER_PID"

    echo pstree -pa $SERVER_PID
    pstree -pa $SERVER_PID

    rm -f oha_output.json
    echo "./oha --http-version=1.1 -n 1000000 -c $NUM_CONNECTIONS --no-tui --output-format json 'http://localhost:8080/test'"
    ./oha --http-version=1.1 -n 1000000 -c $NUM_CONNECTIONS --no-tui --output-format json 'http://localhost:8080/test' | tee oha_output.json

    echo

    SUCCESS_RATE=$(cat oha_output.json | jq '.summary.successRate')
    SUCCESS_RATE=$(bc <<< "scale=1; $SUCCESS_RATE * 100 / 1")
    SUCCESS_RATE="${SUCCESS_RATE}%"
    echo "SUCCESS_RATE = $SUCCESS_RATE"

    TEST_SECONDS=$(cat oha_output.json | jq '.summary.total')
    TEST_SECONDS=$(bc <<< "scale=1; $TEST_SECONDS / 1")
    echo "TEST_SECONDS = $TEST_SECONDS"

    RPS=$(cat oha_output.json | jq '.rps.mean')
    RPS=$(bc <<< "scale=1; $RPS / 1")
    echo "RPS = $RPS"

    REQUEST_P50=$(cat oha_output.json | jq '.latencyPercentiles.p50' )
    REQUEST_P50=$(bc <<< "scale=4; $REQUEST_P50 * 1000 / 1")
    echo "REQUEST_P50 = $REQUEST_P50"

    REQUEST_P99=$(cat oha_output.json | jq '.latencyPercentiles.p99' )
    REQUEST_P99=$(bc <<< "scale=4; $REQUEST_P99 * 1000 / 1")
    echo "REQUEST_P99 = $REQUEST_P99"

    REQUEST_P999=$(cat oha_output.json | jq '.latencyPercentiles."p99.9"' )
    REQUEST_P999=$(bc <<< "scale=4; $REQUEST_P999 * 1000 / 1")
    echo "REQUEST_P999 = $REQUEST_P999"

    SERVER_THREADS=0
    SERVER_PROCESSES=0
    RSS_KB=0
    TOTAL_CPU_TIME="00:00:00"

    for CHILD_PID in $(ps --no-headers -o pid --ppid $SERVER_PID); do
        echo "CHILD_PID=$CHILD_PID"
        SERVER_PROCESSES=$((SERVER_PROCESSES+1))

        echo "ps --no-headers -o pid,cputime,nlwp,rss,cmd -q $CHILD_PID"
        ps --no-headers -o pid,cputime,nlwp,rss,cmd -q $CHILD_PID

        CHILD_THREADS=$(ps -eLf -q $CHILD_PID | grep -v PID | wc -l)
        echo "CHILD_THREADS=$CHILD_THREADS"
        SERVER_THREADS=$((SERVER_THREADS+CHILD_THREADS))

        CHILD_RSS_KB=$(ps -eo pid,user,rss,time -q $CHILD_PID | tail -1 | awk '{print $3}' )
        echo "CHILD_RSS_KB=$CHILD_RSS_KB"
        RSS_KB=$((RSS_KB+CHILD_RSS_KB))

        CHILD_CPU_TIME=$(ps -eo pid,user,rss,time -q $CHILD_PID | tail -1 | awk '{print $4}' )
        echo "CHILD_CPU_TIME=$CHILD_CPU_TIME"
        # sum CPU times
        TOTAL_CPU_TIME=$($SCRIPT_DIR/sum-times.sh $TOTAL_CPU_TIME $CHILD_CPU_TIME)
    done

    PARENT_PID=$SERVER_PID
    echo "PARENT_PID=$PARENT_PID"

    echo "ps --no-headers -o pid,cputime,nlwp,rss,cmd -q $PARENT_PID"
    ps --no-headers -o pid,cputime,nlwp,rss,cmd -q $PARENT_PID

    SERVER_PROCESSES=$((SERVER_PROCESSES+1))
    echo "SERVER_PROCESSES=$SERVER_PROCESSES"

    PARENT_THREADS=$(ps -eLf -q $PARENT_PID | grep -v PID | wc -l)
    echo "PARENT_THREADS=$PARENT_THREADS"
    SERVER_THREADS=$((SERVER_THREADS+PARENT_THREADS))
    echo "SERVER_THREADS=$SERVER_THREADS"

    PARENT_RSS_KB=$(ps -eo pid,user,rss,time -q $PARENT_PID | tail -1 | awk '{print $3}' )
    echo "PARENT_RSS_KB=$PARENT_RSS_KB"
    RSS_KB=$((RSS_KB+PARENT_RSS_KB))
    echo "RSS_KB=$RSS_KB"

    PARENT_CPU_TIME=$(ps -eo pid,user,rss,time -q $PARENT_PID | tail -1 | awk '{print $4}' )
    echo "PARENT_CPU_TIME=$PARENT_CPU_TIME"
    # sum CPU times
    TOTAL_CPU_TIME=$($SCRIPT_DIR/sum-times.sh $TOTAL_CPU_TIME $PARENT_CPU_TIME)
    echo "TOTAL_CPU_TIME=$TOTAL_CPU_TIME"

    RSS_MB=$(bc <<< "scale=1; $RSS_KB / 1000")
    echo "RSS_MB=$RSS_MB"

    # kill child pids
    for CHILD_PID in $(ps --no-headers -o pid --ppid $SERVER_PID); do
        echo "kill child pid $CHILD_PID"
        kill $CHILD_PID
    done

    echo kill $SERVER_PID
    kill $SERVER_PID

    echo "| $TEST_NAME | $NUM_CONNECTIONS | $SUCCESS_RATE | $TEST_SECONDS | $RPS | $REQUEST_P50 | $REQUEST_P99 | $REQUEST_P999 | $RSS_MB | $TOTAL_CPU_TIME | $SERVER_THREADS | $SERVER_PROCESSES |" >> $OUTPUT_FILE

    sleep 1

done

echo "after tests cat $OUTPUT_FILE"
cat $OUTPUT_FILE
