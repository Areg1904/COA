FROM python:3.12

WORKDIR /app

COPY test/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./generated_code ./generated_code
COPY ./test ./test

ENV PYTHONPATH="${PYTHONPATH}:/app/generated_code"

WORKDIR /app/test

CMD ["pytest", "test.py"]
