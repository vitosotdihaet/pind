# Configuration

```
locust -f load-testing/locustfile.py \
    --spawn-rate 10 \
    --autostart \
    --autoquit 0 \
    --html load-testing/results/report.html \
    --users 32 \
    --run-time 120s \
    --processes 16 \
    --config-path load-testing/configs/example.yaml \
    --operation {{ operation }} \
    --index-type {{ index_type }} \
    --admin-password {{ env("ADMIN_PASSWORD") }} \
    --psql-address 127.0.0.1:5433
```
 
```
[tier.pind]
replicasets = 1
replication_factor = 1
```
