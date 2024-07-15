#!/bin/bash
echo "Starting app"
gunicorn -b 0.0.0.0:8085 wsgi:app -D --workers=4 --worker-connections=100 --threads=2 -k gevent_pywsgi
sleep 1
echo "current processes running:"
ps -fea | grep gunicorn
