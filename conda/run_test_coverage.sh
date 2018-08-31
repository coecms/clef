#!/bin/bash
pip install coverage pytest-cov codacy-coverage
py.test --cov=clef --cov-report xml:/tmp/artefacts/pytest/coverage.xml --junit-xml /tmp/artefacts/pytest/results.xml

