FROM python:3

RUN mkdir /app
WORKDIR /app

EXPOSE 5000

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app .
CMD [ "uwsgi", "--ini", "app.ini" ]
