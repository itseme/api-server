.PHONY: clean-pyc ext-test test tox-test test-with-mem upload-docs docs audit

upload-docs:
	$(MAKE) -C docs html dirhtml latex epub
	$(MAKE) -C docs/_build/latex all-pdf
	cd docs/_build/; mv html itseme-docs; zip -r itseme-docs.zip itseme-docs; mv itseme-docs html
	rsync -a docs/_build/dirhtml/ ~/dev/mario/docs
	rsync -a docs/_build/latex/itseme.pdf ~/dev/mario/docs/itseme-docs.pdf
	rsync -a docs/_build/itseme-docs.zip ~/dev/mario/docs/itseme-docs.zip
docs:
	$(MAKE) -C docs html
