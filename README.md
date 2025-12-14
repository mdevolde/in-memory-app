# In-memory-app

## About the Application

This application provides a unified interface to explore and compare the characteristics of different storage backends for event-driven systems. It allows you to interact with either **Memcached** (pure in-memory key-value store) or **SingleStore** (hybrid in-memory database) to understand their respective strengths and limitations.

### Key Features

- **Multiple Backend Support**: Abstracted backend interface supporting Memcached and SingleStore
- **Event Management**: Create, retrieve, and query events with user associations
- **CLI Interface**: Command-line tool for interacting with the backends
- **Batch Operations**: Generate and insert batches of events for testing purposes
- **Hands-on Comparison**: Experiment with both technologies to identify their advantages and drawbacks

### Architecture

The application follows a clean architecture pattern:
- `backend_interface.py`: Abstract interface defining backend operations
- `backends/`: Concrete implementations for Memcached and SingleStore
- `service.py`: Business logic layer for event operations
- `cli.py`: Command-line interface for user interaction
- `data_generator.py`: Synthetic event generation for testing
- `models.py`: Data models for events

### Objectives

- **Identify Strengths**: Discover what Memcached and SingleStore excel at
- **Understand Limitations**: Learn about the constraints and trade-offs of each technology
- **Practical Experience**: Gain hands-on experience with both in-memory and hybrid storage approaches
- **Architecture Decisions**: Help inform storage backend choices for event-driven applications

### Using the Application

#### Installation

First, ensure you have the necessary containers running (see Benchmarks > Prerequisites section).

Install the application dependencies:

```bash
pip install -e .
```

#### CLI Commands

The application provides a command-line interface with the following commands:

##### Add an event

```bash
python ./src/cli.py --backend memcached add-event --user 123 --type "login"
python ./src/cli.py --backend singlestore add-event --user 456 --type "purchase"
```

##### Get an event by ID

```bash
python ./src/cli.py --backend memcached get-event --id "event-uuid-here"
python ./src/cli.py --backend singlestore get-event --id "event-uuid-here"
```

##### List all events for a user

```bash
python ./src/cli.py --backend memcached user-events --user 123
python ./src/cli.py --backend singlestore user-events --user 456
```

##### Generate batch events

```bash
python ./src/cli.py --backend memcached generate-batch --number 100
python ./src/cli.py --backend singlestore generate-batch --number 1000
```

##### Clear all data

```bash
python ./src/cli.py --backend memcached clear-data --confirm
python ./src/cli.py --backend singlestore clear-data --confirm
```

### Retrieve Stored Data

#### Retrieve events in Memcached:

```bash
echo "stats cachedump 5 2000" | nc localhost 11211
```

#### Retrieve events in SingleStore:

```bash
docker exec -it singlestore memsql --user=root --password=test -e "SELECT * FROM test.events;"
```

## Benchmarks

### Prerequisites

First, ensure you have the necessary containers running:

#### Run Memcached

```bash
docker run -d --name memcached -p 11211:11211 memcached memcached -m 256 -t 4
```

#### Run SingleStore

```bash
docker run -d --name singlestore -e ROOT_PASSWORD=test -p 3306:3306 singlestore/cluster-in-a-box:latest
docker start singlestore
```

Create the database "test":

```bash
docker exec -it singlestore memsql --user=root --password=test -e "CREATE DATABASE IF NOT EXISTS test;"
```

#### Run PostgreSQL

```bash
docker run -d \
  --name mypostgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=test \
  -p 5432:5432 \
  postgres:16
```

### Setup YCSB

Clone and build the YCSB project:

```bash
git clone https://github.com/brianfrankcooper/YCSB.git
cd YCSB
```

#### For Memcached:

```bash
mvn -pl memcached -am clean package
```

#### For SingleStore:

```bash
mkdir -p lib
cd lib
wget https://github.com/memsql/S2-JDBC-Connector/releases/download/v1.2.9/singlestore-jdbc-client-1.2.9.jar -O singlestore-jdbc-client-1.2.9.jar
cd ..
mvn -pl jdbc -am clean package
```

Create the table in SingleStore:

```bash
mysql --host=127.0.0.1 --port=3306 --user=root --password=test
```

In the MySQL shell:

```sql
USE test;
CREATE TABLE IF NOT EXISTS usertable (
  YCSB_KEY VARCHAR(255) PRIMARY KEY,
  FIELD0 TEXT,
  FIELD1 TEXT,
  FIELD2 TEXT,
  FIELD3 TEXT,
  FIELD4 TEXT,
  FIELD5 TEXT,
  FIELD6 TEXT,
  FIELD7 TEXT,
  FIELD8 TEXT,
  FIELD9 TEXT
);
EXIT;
```

#### For PostgreSQL:

```bash
mkdir -p lib
cd lib
wget https://jdbc.postgresql.org/download/postgresql-42.7.8.jar
cd ..
mvn -pl jdbc -am clean package
```

Create the table in PostgreSQL:

```bash
docker exec -it mypostgres psql -U postgres -d test
```

In the psql shell:

```sql
CREATE TABLE IF NOT EXISTS usertable (
  ycsb_key VARCHAR(255) PRIMARY KEY,
  field0 TEXT,
  field1 TEXT,
  field2 TEXT,
  field3 TEXT,
  field4 TEXT,
  field5 TEXT,
  field6 TEXT,
  field7 TEXT,
  field8 TEXT,
  field9 TEXT
);
EXIT;
```

### Individual Benchmark Examples

#### Memcached Benchmark (Workload A - Read/Update)

```bash
./bin/ycsb load memcached \
  -P workloads/workloada \
  -p memcached.hosts=127.0.0.1:11211 \
  -s

./bin/ycsb run memcached \
  -P workloads/workloada \
  -p memcached.hosts=127.0.0.1:11211 \
  -threads 10 \
  -s
```

#### Memcached Benchmark (Workload C - Read-only)

```bash
./bin/ycsb run memcached \
  -P workloads/workloadc \
  -p memcached.hosts=127.0.0.1:11211 \
  -threads 10 \
  -s
```

#### SingleStore Benchmark (Workload A)

```bash
./bin/ycsb load jdbc \
  -P workloads/workloada \
  -p db.url="jdbc:singlestore://127.0.0.1:3306/test?user=root&password=test" \
  -p db.driver=com.singlestore.jdbc.Driver \
  -cp lib/singlestore-jdbc-client-1.2.9.jar \
  -p recordcount=10000 \
  -s

./bin/ycsb run jdbc \
  -P workloads/workloada \
  -p db.url="jdbc:singlestore://127.0.0.1:3306/test?user=root&password=test" \
  -p db.driver=com.singlestore.jdbc.Driver \
  -cp lib/singlestore-jdbc-client-1.2.9.jar \
  -p operationcount=10000 \
  -threads 10 \
  -s
```

#### SingleStore Benchmark (Workload C)

```bash
./bin/ycsb run jdbc \
  -P workloads/workloadc \
  -p db.url="jdbc:singlestore://127.0.0.1:3306/test?user=root&password=test" \
  -p db.driver=com.singlestore.jdbc.Driver \
  -cp lib/singlestore-jdbc-client-1.2.9.jar \
  -p operationcount=10000 \
  -threads 10 \
  -s
```

#### PostgreSQL Benchmark (Workload A - Read/Update)

```bash
./bin/ycsb load jdbc \
  -P workloads/workloada \
  -p db.url="jdbc:postgresql://127.0.0.1:5432/test?user=postgres&password=postgres" \
  -p db.driver=org.postgresql.Driver \
  -cp lib/postgresql-42.7.8.jar \
  -p recordcount=10000 \
  -s

./bin/ycsb run jdbc \
  -P workloads/workloada \
  -p db.url="jdbc:postgresql://127.0.0.1:5432/test?user=postgres&password=postgres" \
  -p db.driver=org.postgresql.Driver \
  -cp lib/postgresql-42.7.8.jar \
  -p operationcount=10000 \
  -threads 10 \
  -s
```

#### PostgreSQL Benchmark (Workload C - Read-only)

```bash
./bin/ycsb run jdbc \
  -P workloads/workloadc \
  -p db.url="jdbc:postgresql://127.0.0.1:5432/test?user=postgres&password=postgres" \
  -p db.driver=org.postgresql.Driver \
  -cp lib/postgresql-42.7.8.jar \
  -p operationcount=10000 \
  -threads 10 \
  -s
```

## Benchmark Scripts

This project includes two automated benchmark scripts that simplify the process of running comprehensive performance tests across multiple backends.

### run_benchmarks.sh

This script runs comparative benchmarks across Memcached, SingleStore, and PostgreSQL using the YCSB framework.

#### Configuration

Edit the following parameters in the script:
- `WORKLOADS`: Array of YCSB workloads to test (default: workloada, workloadc)
- `RUNS`: Number of times to repeat each benchmark (default: 3)
- `THREADS`: Number of concurrent threads (default: 10)
- `RECORDCOUNT`: Number of records to load (default: 100000)
- `OPERATIONCOUNT`: Number of operations per run (default: 100000)
- `MEMCACHED_HOSTS`: Memcached server address
- `JDBC_URL`: SingleStore connection string
- `PG_URL`: PostgreSQL connection string

#### Usage

```bash
bash run_benchmarks.sh
```

#### What it does

1. **Runs each workload** (A: read/update, C: read-only) multiple times
2. **Tests all three backends**: Memcached, SingleStore, and PostgreSQL
3. **Extracts metrics**: Throughput, average latency, 95th percentile latency
4. **Generates CSV summary**: Results are saved in `~/Documents/YCSB/results/summary.csv`

### run_scalability.sh

This script performs scalability testing by varying dataset size and thread count.

#### Configuration

Edit the following parameters in the script:
- `WORKLOADS`: Array of YCSB workloads (default: workloada)
- `RECORD_SIZES`: Array of dataset sizes to test (default: 10000, 100000, 1000000)
- `THREADS_LIST`: Array of thread counts (default: 1, 5, 10, 20, 50)
- `RUNS`: Number of repetitions per configuration (default: 3)
- `OPERATIONCOUNT`: Fixed operation count (default: 100000)

#### Usage

```bash
bash run_scalability.sh
```

#### What it does

1. **Tests multiple dataset sizes**: From 10K to 1M records
2. **Varies concurrency levels**: Tests with different thread counts
3. **Compares Memcached vs SingleStore**: Focus on the two main backends
4. **Generates detailed metrics**: Shows how performance scales with load
5. **Creates CSV output**: Results saved in `~/Documents/YCSB/scalability_results/scalability_summary.csv`

