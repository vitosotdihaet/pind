# Configuration

```
for i in "lsi" "gsi"; for j in "search" "insert"; killall picodata && killall locust; just test::load $i $j load-testing/results/medium-low-fk-cardinality/config.yaml 320 true; end; end
```

Users: 320
Replicasets: 8
ReplicationFactor: 1

failed on gsi search, because the keys are too big and fk_cardinality is too small
