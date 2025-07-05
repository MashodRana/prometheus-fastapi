# Dockerfile
FROM python:3.13.1-slim


WORKDIR /code

RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

# CMD ["uvicorn", "app.core.main:get_application", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD alembic upgrade head && python server.py
