set dotenv-required := true
set dotenv-load

import 'tools/build/.justfile'

pind target="debug": (pico::pind target)

build target="debug": (main::build target)

tests cargo_flags="": \
	(test::units cargo_flags) \
	(test::integrations)

clean: pico::clean main::_clean_artifacts

