FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
ADD . /code/
WORKDIR /code

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN ls 
RUN apt-get update 
RUN apt-get -y install build-essential libpqxx-dev postgresql 
RUN apt-get install -y autoconf automake libtool curl make g++

RUN cd pythone && ./configure && make && make install && ldconfig
RUN chmod u+r+x run.sh