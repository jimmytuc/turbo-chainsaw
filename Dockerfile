# alpine issue on libmusl for python performance
FROM python:3.9-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat
RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

COPY scrapyd.conf /etc/scrapyd/

EXPOSE 9000

CMD ["scrapyd"]
