# miscutils

Miscellaneous Python utilities.

## Installation

```console
pip install git+https://github.com/dustinrohde/miscutils.git
```

## Usage

There are no official docs outside of this README yet, but the code is fairly
well documented. I also strongly suggest looking at the [tests](test/) to see
everything in action.

## Overview

Available modules:

- [`case`](miscutils/case.py): tools for formatting strings between various
    cases
- [`envparse`](miscutils/envparse.py): a simple argument parser for
    environment variables
- [`functional`](miscutils/functional.py): functional programming in Python
- [`iters`](miscutils/iters.py): iterator utilities
- [`mappings`](miscutils/mappings.py): various mapping types
- [`merge`](miscutils/merge.py): gracefully merge arbitrarily nested mappings
- [`nested`](miscutils/merge.py): DSL for working with deeply nested data
- [`seq`](miscutils/seq.py): miscellaneous tools for working with sequences
- [`setdefault`](miscutils/setdefault.py): `dict.setdefault` with superpowers
    and generalized to any data type