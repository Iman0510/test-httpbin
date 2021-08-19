#!/usr/bin/env bash

cd /app || exit
gunicorn --workers=1 --bind=0.0.0.0:80 server:app 
