# Configuration

```
for i in "lsi" "gsi"; for j in "search" "insert"; just test::load $i $j load-testing/results/small/config.yaml 320 true; end; end
```

Users: 320
Replicasets: 4
ReplicationFactor: 1
