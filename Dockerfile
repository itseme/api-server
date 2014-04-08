FROM orchardup/python:2.7
MAINTAINER Benjamin Kampmann me|at|create-build-execute|dot|com

RUN apt-get install -qy unzip
RUN mkdir /serf
ADD https://dl.bintray.com/mitchellh/serf/0.5.0_linux_amd64.zip /serf/serf.zip
WORKDIR /serf
RUN unzip serf.zip

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
ADD . /code/

EXPOSE 80
