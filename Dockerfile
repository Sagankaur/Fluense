FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY ["Project Mad1 Git/code/requirements.txt", "/app/requirements.txt"]
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app/Project Mad1 Git/code

EXPOSE 5000

CMD ["python", "app.py"]
