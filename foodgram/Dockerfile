FROM python:3.10

WORKDIR /foodgram
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
