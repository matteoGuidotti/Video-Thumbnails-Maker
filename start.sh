#!/bin/sh
export FLASK_APP=./videoThumbnailsMaker/index.py
pipenv run flask --debug run -h 0.0.0.0
