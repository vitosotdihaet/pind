set working-directory := '../..'

mod main
mod pico

all: units integrations

units flags="":
    bash -c 'set -o pipefail; cargo test {{ flags }}'

_run_storage topology:
    just pind release {{ topology }} && just pico::set_admin_pass

integrations start_storage="true": (main::_check_arg start_storage "true" "false")
    error("not implemented")

load config:
    #!/usr/bin/env bash
    config_prefix=load-testing/results/{{ config }}
    topology=$config_prefix/topology.toml
    config=$config_prefix/config.yaml

    # TODO: move out to another recipe
    PIND_CONFIG="../$config" jupyter execute math-model-calculations/main.ipynb &

    # for op in "search" "insert"
    for op in "search"; do \
        just test::_run_storage $topology; \
        sleep 5; \
        for index in "lsi" "gsi"; do \
            locust -f load-testing/locustfile.py \
                --spawn-rate 4 \
                --autostart \
                --autoquit 0 \
                --users 100 \
                --run-time 120s \
                --processes 16 \
                --config-path $config \
                --operation $op \
                --index-type $index \
                --html $config_prefix/report_${op}_${index}.html \
                --admin-password {{ env("ADMIN_PASSWORD") }} \
                --psql-address 127.0.0.1:5433 || true; \
        done \
    done

    just pico::down
