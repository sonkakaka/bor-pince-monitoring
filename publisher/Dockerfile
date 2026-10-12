FROM python:3.11-slim

WORKDIR /app

COPY publisher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY publisher/publisher.py .
COPY simulator/szimulator.py .

ENV PYTHONPATH=/app

CMD ["python", "-u", "publisher.py"]