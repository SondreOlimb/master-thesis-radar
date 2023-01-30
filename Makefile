makeFileDir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))


run:
	python3 client.py


.PHONY: run