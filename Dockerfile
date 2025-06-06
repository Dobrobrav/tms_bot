FROM python:3.13

COPY /. /usr/src/app
WORKDIR /usr/src/app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]