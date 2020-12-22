#!/bin/sh
source .venv/bin/activate
while true; do
    echo Upgrading database
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done

# while true; do
#     echo reindexing Elasticsearch
#     flask search reindex
#     if [[ "$?" == "0" ]]; then
#         break
#     fi
#     echo Reindex command failed, retrying in 5 secs...
#     sleep 5
# done

# https://pythonspeed.com/articles/gunicorn-in-docker/
exec gunicorn -b :5000 --worker-tmp-dir /dev/shm -w 2 --threads=4 --worker-class=gthread --timeout 5 \
        --access-logfile - --error-logfile - microblog:app