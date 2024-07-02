#!/bin/sh
# See https://packaging.python.org/en/latest/tutorials/packaging-projects/
rm dist/*
python3 -m build
python3 -m twine upload dist/*

