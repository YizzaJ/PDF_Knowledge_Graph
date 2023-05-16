#!/bin/bash
docker rm group3/app

docker build -t group3/app -f App/dockerfile .

docker run --rm -it -p 8080:8080 --name flask group3/app