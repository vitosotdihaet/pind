set working-directory := '../..'

mod main

clean:
	{{ env("PIKE_BINARY_PATH") }} clean

down:
	{{ env("PIKE_BINARY_PATH") }} stop

config path="./configs/default.yaml":
	{{ env("PIKE_BINARY_PATH") }} config apply \
		--config-path={{ path }}

set_admin_pass:
	echo "alter user admin with password '{{ env("ADMIN_PASSWORD") }}'" | cargo pike enter --picodata-path={{ env("PICODATA_BINARY_PATH") }} i1

up target="debug": (main::_check_arg target "debug" "release")
	#!/usr/bin/env bash
	set -euo pipefail

	if [ "{{ target }}" == "release" ]; then
		release="--release"
	else
		release=""
	fi

	RUST_BACKTRACE=full \
	RUST_LIB_BACKTRACE=0 \
	{{ env("PIKE_BINARY_PATH") }} run \
		--picodata-path={{ env("PICODATA_BINARY_PATH") }} \
		--no-build \
		--daemon \
		$release

pind target="debug": (main::_check_arg target "debug" "release") clean && (up target) wait_till_rebalance_is_done main::_wait
	#!/usr/bin/env bash
	set -euo pipefail

	if [ "{{ target }}" == "release" ]; then
		just main::build release
	else
		just main::build
	fi

wait_till_rebalance_is_done:
	#!/usr/bin/env bash
	for i in $(ls -d tmp/cluster/i*); do

	cat <<'EOF' | cargo pike enter ${i//tmp\/cluster\//}
	\lua;
	while (box.space._pico_tier:get{pico.whoami().tier}.bucket_count / pico.sql("select count(*) from _pico_replicaset where tier = '" .. pico.whoami().tier .. "'").rows[1][1]) ~= box.space._bucket:count() do require('fiber').sleep(0.1) end
	EOF
	done

fill_with_some_data amount="100":
	#!/usr/bin/env bash
	SOCK="./tmp/cluster/i1/admin.sock"
	sql="create table if not exists _pind_test_table (a int primary key) distributed by (a) in tier pind;"
	for i in $(seq 1 {{ amount }}); do
		sql="$sql insert into _pind_test_table values ($i);"
	done
	echo "$sql" | picodata admin "$SOCK" > /dev/null


