#!/bin/bash

docker run --rm -p 8070:8070 --name grobid -d lfoppiano/grobid:0.7.2

sleep 3

docker rm group3/preprocess

docker build --tag group3/preprocess .

docker run --rm -it -v $(pwd)/templates/:/app/templates -v $(pwd)/static/:/app/static -v $(pwd)/CSV/:/app/CSV -v $(pwd)/output/:/app/output --name preprocess --network=host group3/preprocess

docker stop grobid

pause