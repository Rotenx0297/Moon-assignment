FROM rotenx0297/rotem-base:latest
WORKDIR /app
COPY . /app
RUN sudo pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/check_sqs_policy.py
ENTRYPOINT ["python", "/app/check_sqs_policy.py"]
