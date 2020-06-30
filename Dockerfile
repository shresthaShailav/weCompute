# ubuntu
FROM ubuntu:16.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y docker

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip3 install -r requirements.txt

COPY ./src /app
WORKDIR /app

ENV APP_PATH="/app"
ENV WAIT_INTERVAL="10"
#ENV SELF_ID="DV_0003_"
#ENV HOST="http://localhost:4500"

CMD python3 main.py
