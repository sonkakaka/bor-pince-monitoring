FROM python:3.11-slim

WORKDIR /app

COPY subscriber/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY subscriber/subscriber.py .

CMD ["python", "-u", "subscriber.py"]