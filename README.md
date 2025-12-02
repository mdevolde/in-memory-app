# In-memory-app

## Retrieve existing events in Memcached

```bash
echo "stats cachedump 5 2000" | nc localhost 11211
```

## Retrieve existing events in SingleStore

```bash
docker exec -it singlestore memsql --user=root --password=test -e "SELECT * FROM test.events;"
```
