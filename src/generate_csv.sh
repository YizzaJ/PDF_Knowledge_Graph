#!/bin/bash
docker rm group3/generate_csv

docker build -t group3/generate_csv -f generate_csv\dockerfile .

docker run --rm -it -v $(pwd)/CSV/:/app/CSV -v $(pwd)/output/:/app/output --name generate_csv --network=host group3/generate_csv

pause