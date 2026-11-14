FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY bot/ /app/

EXPOSE 8080

CMD ["gunicorn", "-w", "1", "--threads", "4", "-b", "0.0.0.0:8080", "--timeout", "30", "--access-logfile", "-", "bot:bot"]
