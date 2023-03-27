makeFileDir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))


run:
	python3 client.py
activate:
	source env/bin/activate


.PHONY: run, activate