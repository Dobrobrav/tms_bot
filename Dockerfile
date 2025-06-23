FROM python:3.13

COPY /. /usr/src
WORKDIR /usr/src

RUN pip install -r requirements.txt

WORKDIR /usr/src/app
ENTRYPOINT ["python3", "main.py"]