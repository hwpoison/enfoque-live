#!/bin/bash
echo "Starting app"
gunicorn -b 0.0.0.0:443 --certfile /etc/letsencrypt/live/vps-4014146-x.dattaweb.com/cert.pem --keyfile /etc/letsencrypt/live/vps-4014146-x.dattaweb.com/privkey.pem wsgi:app -D --workers=4
sleep 1

#if pgrep -x "gunicorn" > /dev/null
#then
#    echo "gunicorn successfully started"
#    nohup python3 hls_compressor.py > /dev/null 1>&1 &
#    echo "hls_compress started"
#else
#    echo "Failed to start gunicorn, hls_compress not started"
#fi

echo "current processes running:"
ps -fea | grep gunicorn
ps -fea | grep python
