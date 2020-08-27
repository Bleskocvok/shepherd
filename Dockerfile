
FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt

CMD python3 ftp-harvest/run.py -l && { python3 ftp-harvest/run.py -b 30 & python3 ./run.py; }

