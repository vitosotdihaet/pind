set working-directory := '../..'

build target="debug": (_check_arg target "debug" "release")
	cargo build {{ if target == "release" { "--release" } else { "" } }}

rebuild target="debug": _clean_artifacts (build target)

_wait:
	#!/usr/bin/env bash
	set -eo pipefail
	wait_time=10
	sleep $wait_time

_check_arg value *valid:
	#!/usr/bin/env bash
	set -euo pipefail
	for str in {{ valid }}; do
		if [ "$str" == "{{ value }}" ]; then
			exit 0
		fi
	done
	echo '"`{{ value }}`" is not found in valid values list: `{{ valid }}`'
	exit 1

_clean_artifacts:
	cargo clean
