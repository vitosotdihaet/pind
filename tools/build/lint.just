set working-directory := '../..'

lint: cargo

cargo:
	cargo check
	cargo fmt --all -- --check
	cargo clippy -- -Dclippy::all -Wclippy::pedantic --deny "warnings" --no-deps

cargo-fix:
	cargo fmt --all
	cargo clippy --fix

fix: cargo-fix

pre-commit: fix lint
