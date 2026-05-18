# Configuration

```
for i in "lsi" "gsi"; for j in "search" "insert"; killall picodata && killall locust; just test::load $i $j load-testing/results/medium/config.yaml 640 true; end; end
```

Users: 640
Replicasets: 8
ReplicationFactor: 1
