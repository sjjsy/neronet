#!/bin/bash
cpdfs *.md *.tex diaries/*.tex
zip required_artifacts.zip product_vision.pdf process_overview.pdf technical_overview.pdf definition_of_done.pdf progress_report.pdf test_session_charter.pdf
