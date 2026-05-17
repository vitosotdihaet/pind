set working-directory := '../..'

mod main
mod pico

all: units integrations

units flags="":
    bash -c 'set -o pipefail; cargo test {{ flags }}'

_run_storage:
    just pind release

integrations start_storage="true": (main::_check_arg start_storage "true" "false")
    error("not implemented")

load index_type operation start_storage="true": (main::_check_arg start_storage "true" "false")
    #!/usr/bin/env bash
    if [ "{{ start_storage }}" == "true" ]; then
        just test::_run_storage
    fi
    locust -f load-testing/locustfile.py \
        --config-path load-testing/configs/example.yaml \
        --index-type {{ index_type }} \
        --operation {{ operation }} \
        --spawn-rate 10 \
        --autostart \
        --users 1600 \
        --run-time 300s \
        --processes 16 \
        --hosts http://127.0.0.1:8001 http://127.0.0.1:8002 http://127.0.0.1:8003 http://127.0.0.1:8004 http://127.0.0.1:8005
    # TODO: use python driver to get all hostnames
    # TODO: use config files for locust
