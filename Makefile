webserver:
	python -m SimpleHTTPServer 8001


# ------
# Common
# ------
$(eval venvpath     := .venv27)
$(eval bumpversion  := $(venvpath)/bin/bumpversion)


# -------
# Release
# -------

bumpversion:
	$(bumpversion) $(bump)

push:
	git push && git push --tags

release: bumpversion push


# -------------
# Documentation
# -------------

docs-virtualenv:
	$(eval venvpath := ".venv_sphinx")
	@test -e $(venvpath)/bin/python || `command -v virtualenv` --python=`command -v python` --no-site-packages $(venvpath)
	@$(venvpath)/bin/pip --quiet install --requirement requirements-docs.txt

docs-html: docs-virtualenv
	$(eval venvpath := ".venv_sphinx")
	touch doc/index.rst
	export SPHINXBUILD="`pwd`/$(venvpath)/bin/sphinx-build"; cd doc; make html
