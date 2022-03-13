FROM python:3.9

ENV PYTHONUNBUFFERED=1

COPY . /app
WORKDIR /app

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN pip3 install -r /app/requirements.txt
RUN mkdir /app/data

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
