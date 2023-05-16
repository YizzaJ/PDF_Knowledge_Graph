title Docker file

docker run --rm -p 8070:8070 --name grobid -d lfoppiano/grobid:0.7.2

SLEEP 3

docker rm group3/preprocess

docker build --tag group3/preprocess .

docker run --rm -it -v %cd%\templates\:/app/templates -v %cd%\static\:/app/static -v %cd%\CSV\:/app/CSV -v %cd%\output\:/app/output --name preprocess --network=host group3/preprocess

docker stop grobid

pause