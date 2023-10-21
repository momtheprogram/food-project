FROM python:3.11-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi:application"]
