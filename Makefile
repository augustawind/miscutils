.PHONY: docs
docs:
	sphinx-apidoc --force --separate --module-first -a -o docs/ .
