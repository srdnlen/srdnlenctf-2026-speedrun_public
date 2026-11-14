FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "--threads", "8", "-b", "0.0.0.0:5000", "--timeout", "30", "--keep-alive", "75", "--access-logfile", "-", "app:app"]
