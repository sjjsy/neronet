# Makefile for documentation
#

# Variables
SPHINXOPTS = -d ./build/doctrees ./source

.PHONY: help clean sphinxdoc artifacts

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  sphinxdoc       to make standalone HTML documentation"
	@echo "  artifacts         to compile all artifacts to PDF"

clean:
	rm -rf build/*

sphinxdoc:
	sphinx-apidoc -f -o ./source ../neronet
	sphinx-build -b html $(SPHINXOPTS) ./build/html
	@echo
	@echo "Build finished. The HTML pages are in ./build/html."

artifacts:
	@echo "Compiling all updated artifacts."
	cpdfs *.md *.tex diaries/*.tex
	zip required_artifacts.zip product_vision.pdf process_overview.pdf \
	  technical_overview.pdf definition_of_done.pdf progress_report.pdf \
	  test_session_charter.pdf
	@echo "Compilation finished."
