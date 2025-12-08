#!/usr/bin/env bash
set -euo pipefail

########################
# GLOBAL CONFIGURATION
########################
YCSB_DIR="$HOME/Documents/YCSB"
RESULTS_DIR="$YCSB_DIR/results"
mkdir -p "$RESULTS_DIR"

# Workloads to run
WORKLOADS=(workloada workloadc)

# How many times to repeat each run
RUNS=3

# YCSB parameters
THREADS=10
RECORDCOUNT=100000
OPERATIONCOUNT=100000

# Memcached
MEMCACHED_HOSTS="127.0.0.1:11211"

# SingleStore (JDBC)
JDBC_URL='jdbc:singlestore://127.0.0.1:3306/test?user=root&password=test'
JDBC_DRIVER='com.singlestore.jdbc.Driver'
JDBC_JAR="$YCSB_DIR/lib/singlestore-jdbc-client-1.2.9.jar"

SUMMARY_CSV="$RESULTS_DIR/summary.csv"

cd "$YCSB_DIR"

########################
# Execution Functions
########################

run_memcached() {
  local workload=$1
  local run_id=$2

  # load only on the first run for this workload
  if [[ "$run_id" -eq 1 ]]; then
    echo "===> [memcached][$workload] LOAD (recordcount=$RECORDCOUNT)"
    ./bin/ycsb load memcached \
      -P "workloads/${workload}" \
      -p "memcached.hosts=${MEMCACHED_HOSTS}" \
      -p "recordcount=${RECORDCOUNT}" \
      -s \
      | tee "$RESULTS_DIR/memcached_${workload}_load.log"
  fi

  local log="$RESULTS_DIR/memcached_${workload}_run${run_id}.log"
  echo "===> [memcached][$workload] RUN #$run_id (operationcount=$OPERATIONCOUNT)"
  ./bin/ycsb run memcached \
    -P "workloads/${workload}" \
    -p "memcached.hosts=${MEMCACHED_HOSTS}" \
    -p "operationcount=${OPERATIONCOUNT}" \
    -threads "${THREADS}" \
    -s \
    | tee "$log"

  extract_metrics "memcached" "$workload" "$run_id" "$log"
}

run_jdbc() {
  local workload=$1
  local run_id=$2

  # load only on the first run for this workload
  if [[ "$run_id" -eq 1 ]]; then
    echo "===> [singlestore][$workload] LOAD (recordcount=$RECORDCOUNT)"
    ./bin/ycsb load jdbc \
      -P "workloads/${workload}" \
      -p "db.url=${JDBC_URL}" \
      -p "db.driver=${JDBC_DRIVER}" \
      -cp "${JDBC_JAR}" \
      -p "recordcount=${RECORDCOUNT}" \
      -s \
      | tee "$RESULTS_DIR/singlestore_${workload}_load.log"
  fi

  local log="$RESULTS_DIR/singlestore_${workload}_run${run_id}.log"
  echo "===> [singlestore][$workload] RUN #$run_id (operationcount=$OPERATIONCOUNT)"
  ./bin/ycsb run jdbc \
    -P "workloads/${workload}" \
    -p "db.url=${JDBC_URL}" \
    -p "db.driver=${JDBC_DRIVER}" \
    -cp "${JDBC_JAR}" \
    -p "operationcount=${OPERATIONCOUNT}" \
    -threads "${THREADS}" \
    -s \
    | tee "$log"

  extract_metrics "singlestore" "$workload" "$run_id" "$log"
}

########################
# Extract Metrics Function
########################

extract_metrics() {
  local db=$1
  local workload=$2
  local run=$3
  local log=$4

  # Create CSV header if it doesn't exist
  if [[ ! -f "$SUMMARY_CSV" ]]; then
    echo "db,workload,run,throughput_ops_per_sec,read_avg_us,read_95_us,update_avg_us,update_95_us" > "$SUMMARY_CSV"
  fi

  # Overall throughput
  local throughput
  throughput=$(grep "\[OVERALL\], Throughput(ops/sec)" "$log" | awk -F, '{gsub(/ /,"",$3); print $3}')

  # READ metrics
  local read_avg read_95
  read_avg=$(grep "\[READ\], AverageLatency(us)" "$log" | awk -F, '{gsub(/ /,"",$3); print $3}')
  read_95=$(grep "\[READ\], 95thPercentileLatency(us)" "$log" | awk -F, '{gsub(/ /,"",$3); print $3}')

  # UPDATE metrics (there may not be any in workloadC, so we protect a bit)
  local update_avg="" update_95=""
  if grep -q "\[UPDATE\], AverageLatency(us)" "$log"; then
    update_avg=$(grep "\[UPDATE\], AverageLatency(us)" "$log" | awk -F, '{gsub(/ /,"",$3); print $3}')
    update_95=$(grep "\[UPDATE\], 95thPercentileLatency(us)" "$log" | awk -F, '{gsub(/ /,"",$3); print $3}')
  fi

  echo "$db,$workload,$run,$throughput,$read_avg,$read_95,$update_avg,$update_95" >> "$SUMMARY_CSV"
}

########################
# Main Loop
########################

for workload in "${WORKLOADS[@]}"; do
  for run in $(seq 1 "$RUNS"); do
    # You can swap the order if you want
    run_memcached "$workload" "$run"
    run_jdbc "$workload" "$run"
  done
done

echo "Benchmarks completed. Summary available at $SUMMARY_CSV"
