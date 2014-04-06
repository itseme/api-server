FROM orchardup/python:2.7
MAINTAINER Benjamin Kampmann me|at|create-build-execute|dot|com

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
ADD . /code/
