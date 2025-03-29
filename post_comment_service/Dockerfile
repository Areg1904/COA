FROM python:3.12

WORKDIR /app

COPY post_comment_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./generated_code ./generated_code
COPY ./post_comment_service ./post_comment_service

ENV PYTHONPATH="${PYTHONPATH}:/app/generated_code"

WORKDIR /app/post_comment_service

EXPOSE 8002

CMD ["python", "main.py"]
