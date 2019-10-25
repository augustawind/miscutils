.PHONY: fmt
fmt:
	pyfmt --line-length 79

.PHONY: test
test:
	python -m pytest $(if $DEBUG,-s) $(if $V,-vv) $(ARGS)

.PHONY: check
check: fmt test

.PHONY: docs
docs:
	sphinx-apidoc --force --separate --module-first -a -o docs/ .
