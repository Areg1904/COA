FROM python:3.12

WORKDIR /app

COPY api_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./generated_code ./generated_code
COPY ./api_gateway ./api_gateway

ENV PYTHONPATH="${PYTHONPATH}:/app/generated_code"

WORKDIR /app/api_gateway

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
