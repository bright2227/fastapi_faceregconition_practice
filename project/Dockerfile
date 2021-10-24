# pull official base image
FROM animcogn/face_recognition:gpu

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update
RUN apt-get -y install netcat gcc postgresql
RUN apt-get install redis
RUN apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .

# start redis
RUN mkdir /var/run/redis
RUN touch /var/run/redis/redis-server.sock
RUN redis-server ./redis/redis.conf

# start celery
RUN celery --app=app.worker worker --detach
