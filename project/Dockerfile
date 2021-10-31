# pull base image
FROM bright2227/face_recognition:cpu

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update
RUN apt-get -y install procps redis vim
RUN apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .
RUN mkdir /var/run/redis
RUN touch /var/run/redis/redis-server.sock

ENTRYPOINT [ "./entrypoint.sh" ]