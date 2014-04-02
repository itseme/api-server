FROM orchardup/python:2.7
MAINTAINER Benjamin Kampmann me|at|create-build-execute|dot|com

ADD https://github.com/itseme/api-server/archive/master.tar.gz /
RUN tar xf master.tar.gz
RUN mv /api-server-master/ /app/
WORKDIR /app
RUN pip install -r requirements.txt

WORKDIR /app
ENTRYPOINT ["python", "main.py"]
#USER deamon

EXPOSE 5000
