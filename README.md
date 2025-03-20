# fecatq

Introduces the python package `fecatq` for (fe) Fair-Ease (cat) CATalog (q) Querying.

It uses `sema.query` and some own established query-templates to perform a number of dedicated lookups into the IDDAS Asset Catalog from the command-line.

## dependencies

We use [python](https://www.python.org/), and [poetry](https://python-poetry.org/docs/). You will need those to use this.

We recommend using git+ssh -- see [documentation on how to use ssh when connecting to github](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

## install

```bash
$ git clone git@github.com:fair-ease/py-iddas-query.git
$ cd py-iddas-query
$ poetry install
$ poetry run iddas

```

## use

## self-help

The cli tool supports `--help` on various levels to help discover what can be done.

```bash
$ poetry run iddas --help
$ poetry run iddas ls --help
$ poetry run iddas qry --help
```

## available queries:

Note: get the build-in list of available queries with `poetry run iddas list`

### describe

This will "describe" a passed `--var subject «subject-uri-here»` -- i.e. list available `?predicate ?object` combinations associated to it

### wms

List services in the IDDAS that match (conform to) the WMS protocol
