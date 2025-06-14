#!/bin/bash
export ENV=prod
gunicorn -c gunicorn.conf.py app.main:app
