webserver:
	python -m SimpleHTTPServer 8001

$(eval venvpath     := .venv27)
$(eval bumpversion  := $(venvpath)/bin/bumpversion)
bumpversion:
	$(bumpversion) $(bump)

push:
	git push && git push --tags

release: bumpversion push
