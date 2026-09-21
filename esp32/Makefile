# ESP32-CYD standalone
.PHONY: build build-all test contract upload monitor simulator publish

export PATH := $(HOME)/.local/bin:$(PATH)

build:
	pio run -e cyd

build-all:
	pio run -e cyd -e cyd-noled

contract:
	python3 tests/test_grok_contract.py

test: contract

upload:
	pio run -e cyd -t upload

monitor:
	pio device monitor -e cyd

simulator:
	cd simulator && python3 -m http.server 8765

publish:
	./scripts/publish-github.sh
