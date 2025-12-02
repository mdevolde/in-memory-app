# In-memory-app

## Run docker containers
### Run Memcached

```bash
docker run -d --name memcached -p 11211:11211 memcached memcached -m 256 -t 4
```

### Run SingleStore

```bash
docker run -d --name singlestore -e ROOT_PASSWORD=test -p 3306:3306 singlestore/cluster-in-a-box:latest
docker start singlestore
```

Be sure to create the database "test" before running the application:

```bash
docker exec -it singlestore memsql --user=root --password=test -e "CREATE DATABASE IF NOT EXISTS test;"
```

## Retrieve existing lines created by the application
### Retrieve existing events in Memcached

```bash
echo "stats cachedump 5 2000" | nc localhost 11211
```

### Retrieve existing events in SingleStore

```bash
docker exec -it singlestore memsql --user=root --password=test -e "SELECT * FROM test.events;"
```

## Benchmarks

### Isolated Memcached benchmark

```bash
git clone https://github.com/brianfrankcooper/YCSB.git
cd YCSB
mvn -pl memcached -am clean package

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

Other possible benchmark : 
```bash
./bin/ycsb run memcached \
  -P workloads/workloadc \
  -p memcached.hosts=127.0.0.1:11211 \
  -threads 10 \
  -s
```

### Isolated Singlestore benchmark

```bash
git clone https://github.com/brianfrankcooper/YCSB.git
cd YCSB
mkdir -p lib
cd lib
wget https://github.com/memsql/S2-JDBC-Connector/releases/download/v1.2.9/singlestore-jdbc-client-1.2.9.jar -O singlestore-jdbc-client-1.2.9.jar
cd ..
mvn -pl jdbc -am clean package
mysql --host=127.0.0.1 --port=3306 --user=root --password
```

Once you are in the MySQL shell, create the table:

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

Then run the benchmark:

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

Other possible benchmark : 
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
