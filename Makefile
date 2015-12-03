# Neronet makefile
#
# Variables
SPHINXOPTS = -d ./doc/build/doctrees ./doc/source

.PHONY: help clean codedoc artifacts

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  codedoc       to generate HTML code documentation"
	@echo "  artifacts     to compile all artifacts to PDF"

clean:
	rm -rf ./doc/build/*

codedoc:
	sphinx-build -b html $(SPHINXOPTS) ./doc/build/html
	@echo
	@echo "Build finished. The HTML pages are in ./doc/build/html."

artifacts:
	@echo "Compiling all updated artifacts."
	cpdfs ./doc/*.md ./doc/*.tex ./doc/diaries/*.tex
	zip ./doc/required_artifacts.zip \
	  ./doc/product_vision.pdf \
	  ./doc/process_overview.pdf \
	  ./doc/technical_overview.pdf \
	  ./doc/definition_of_done.pdf \
	  ./doc/progress_report.pdf \
	  ./doc/test_session_charter.pdf
	@echo "Compilation finished."
