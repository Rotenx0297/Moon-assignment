FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/check_sqs_policy.py
ENTRYPOINT ["python", "/app/check_sqs_policy.py"]
