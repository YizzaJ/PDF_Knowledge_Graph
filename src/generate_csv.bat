title Docker file

docker rm group3/generate_csv

docker build -t group3/generate_csv -f generate_csv\dockerfile .

docker run --rm -it -v %cd%\CSV\:/app/CSV -v %cd%\output\:/app/output --name generate_csv --network=host group3/generate_csv

pause