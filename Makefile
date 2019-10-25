.PHONY: fmt
fmt:
	pyfmt --line-length 79 --extra-black-args='--exclude=docs/' --extra-isort-args='--skip docs/'

.PHONY: test
test:
	python -m pytest $(if $DEBUG,-s) $(if $V,-vv) $(ARGS)

.PHONY: check
check: fmt test

.PHONY: docs
docs:
	cd docs/ && make html
