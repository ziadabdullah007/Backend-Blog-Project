FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requierments.txt .
RUN pip install --no-cache-dir -r requierments.txt

COPY . .

RUN mkdir -p logs frontend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]