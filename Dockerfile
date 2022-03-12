FROM python:3.9-alpine

ENV PYTHONIOENCODING=utf-8

COPY . /app
WORKDIR /app

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
