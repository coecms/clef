#!/bin/bash
pip install coverage pytest-cov codacy-coverage
py.test --cov=clef --cov-report xml
python-codacy-coverage -r coverage.xml

