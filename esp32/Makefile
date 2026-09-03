# ESP32 PoP-SE companion — atalhos locais
.PHONY: build build-all test contract upload-dev monitor-dev publish

export PATH := $(HOME)/.local/bin:$(PATH)

build:
	pio run -e esp32dev

build-all:
	pio run -e esp32dev -e esp32-s3 -e esp32-c3 -e lilygo-t-display-s3

contract:
	python3 tests/test_popse_contract.py

test: contract build-all

upload-dev:
	pio run -e esp32dev -t upload

monitor-dev:
	pio device monitor -e esp32dev

publish:
	./scripts/publish-github.sh
