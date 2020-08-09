FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /
RUN pip3 install --no-cache --upgrade -r requirements.txt

COPY objects/ /app
WORKDIR /app

ENTRYPOINT ["/bin/bash"]