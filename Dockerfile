FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Moscow

COPY . /app
WORKDIR /app

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN pip3 install -r /app/requirements.txt
RUN mkdir /app/data

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
