#!/usr/bin/env bash
set -euo pipefail

########################
# GLOBAL CONFIGURATION
########################
YCSB_DIR="$HOME/Documents/YCSB"
RESULTS_DIR="$YCSB_DIR/scalability_results"
mkdir -p "$RESULTS_DIR"

WORKLOADS=(workloada)

# Scalability parameters
RECORD_SIZES=(10000 100000 1000000)
THREADS_LIST=(1 5 10 20 50)
RUNS=3

# Fixed operation count for fairness
OPERATIONCOUNT=100000

# Memcached
MEMCACHED_HOSTS="127.0.0.1:11211"

# SingleStore
JDBC_URL='jdbc:singlestore://127.0.0.1:3306/test?user=root&password=test'
JDBC_DRIVER='com.singlestore.jdbc.Driver'
JDBC_JAR="$YCSB_DIR/lib/singlestore-jdbc-client-1.2.9.jar"

SUMMARY_CSV="$RESULTS_DIR/scalability_summary.csv"

cd "$YCSB_DIR"

########################
# Execution Functions
########################

run_memcached() {
  local workload=$1
  local rec=$2
  local th=$3
  local run_id=$4

  # Fresh load for each dataset size
  if [[ "$run_id" -eq 1 ]]; then
    echo "=== [memcached][$workload] LOAD ($rec records)"
    ./bin/ycsb load memcached \
      -P workloads/$workload \
      -p memcached.hosts=$MEMCACHED_HOSTS \
      -p recordcount=$rec \
      -s | tee "$RESULTS_DIR/memcached_${workload}_${rec}_load.log"
  fi

  local log="$RESULTS_DIR/memcached_${workload}_${rec}_${th}_run${run_id}.log"
  echo "=== [memcached][$workload] RUN rec=$rec th=$th run=$run_id"
  ./bin/ycsb run memcached \
    -P workloads/$workload \
    -p memcached.hosts=$MEMCACHED_HOSTS \
    -p operationcount=$OPERATIONCOUNT \
    -threads $th \
    -s | tee "$log"

  extract_metrics "memcached" "$workload" "$rec" "$th" "$run_id" "$log"
}

run_singlestore() {
  local workload=$1
  local rec=$2
  local th=$3
  local run_id=$4

  if [[ "$run_id" -eq 1 ]]; then
    echo "=== [singlestore][$workload] LOAD ($rec records)"
    ./bin/ycsb load jdbc \
      -P workloads/$workload \
      -p db.url=$JDBC_URL \
      -p db.driver=$JDBC_DRIVER \
      -cp $JDBC_JAR \
      -p recordcount=$rec \
      -s | tee "$RESULTS_DIR/singlestore_${workload}_${rec}_load.log"
  fi

  local log="$RESULTS_DIR/singlestore_${workload}_${rec}_${th}_run${run_id}.log"
  echo "=== [singlestore][$workload] RUN rec=$rec th=$th run=$run_id"

  ./bin/ycsb run jdbc \
    -P workloads/$workload \
    -p db.url=$JDBC_URL \
    -p db.driver=$JDBC_DRIVER \
    -cp $JDBC_JAR \
    -p operationcount=$OPERATIONCOUNT \
    -threads $th \
    -s | tee "$log"

  extract_metrics "singlestore" "$workload" "$rec" "$th" "$run_id" "$log"
}

########################
# Extract Metrics
########################

extract_metrics() {
  local db=$1
  local workload=$2
  local rec=$3
  local th=$4
  local run=$5
  local log=$6

  if [[ ! -f "$SUMMARY_CSV" ]]; then
    echo "db,workload,recordcount,threads,run,throughput,read_avg,read_95,update_avg,update_95" > "$SUMMARY_CSV"
  fi

  local throughput
  throughput=$(grep "\[OVERALL\], Throughput" "$log" | awk -F, '{print $3+0}')

  local read_avg read_95 update_avg update_95
  read_avg=$(grep "\[READ\], AverageLatency" "$log" | awk -F, '{print $3+0}')
  read_95=$(grep "\[READ\], 95thPercentileLatency" "$log" | awk -F, '{print $3+0}')
  update_avg=$(grep "\[UPDATE\], AverageLatency" "$log" | awk -F, '{print $3+0}')
  update_95=$(grep "\[UPDATE\], 95thPercentileLatency" "$log" | awk -F, '{print $3+0}')

  echo "$db,$workload,$rec,$th,$run,$throughput,$read_avg,$read_95,$update_avg,$update_95" \
    >> "$SUMMARY_CSV"
}

########################
# Main Loop
########################

for workload in "${WORKLOADS[@]}"; do
  for rec in "${RECORD_SIZES[@]}"; do
    for th in "${THREADS_LIST[@]}"; do
      for run in $(seq 1 $RUNS); do
        run_memcached "$workload" "$rec" "$th" "$run"
        run_singlestore "$workload" "$rec" "$th" "$run"
      done
    done
  done
done

echo "Scalability benchmarks completed."
echo "Summary available at: $SUMMARY_CSV"
