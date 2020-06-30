FROM ubuntu:16.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip3 install -r requirements.txt

WORKDIR /app
COPY ./src /app

EXPOSE 5000
CMD ["python3", "app.py"]
