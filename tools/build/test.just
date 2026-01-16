set working-directory := '../..'

mod main
mod pico

all: units integrations

units flags="":
	bash -c 'set -o pipefail; cargo test {{ flags }}'

_run_storage:
	just pico::up

integrations start_storage="true": \
	(main::_check_arg start_storage "true" "false")
	error("not implemented")
