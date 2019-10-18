.PHONY: test
test:
	python -m pytest $(if $DEBUG,-s) $(if $V,-vv)

.PHONY: docs
docs:
	sphinx-apidoc --force --separate --module-first -a -o docs/ .
