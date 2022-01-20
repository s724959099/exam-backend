FROM python:3.8
ENV ENV dev
ENV TZ Asia/Taipei
ARG TAG
ARG TAG=dev-0.0.1
ENV TAG ${TAG}
COPY ./app /app
WORKDIR /app

RUN pip install -r requirements.txt