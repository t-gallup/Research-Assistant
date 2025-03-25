# Use Python 3.11 image with a newer Linux base
FROM python:3.11-bullseye

# Create app directory
WORKDIR /var/task

# Install AWS Lambda Runtime Interface Client
RUN pip install --no-cache-dir awslambdaric

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY *.py .

# Copy Firebase credentials and verify the file exists
COPY firebase-adminsdk.json ./firebase-adminsdk.json
RUN ls -la /var/task/firebase-adminsdk.json && \
    chmod 644 /var/task/firebase-adminsdk.json && \
    echo "Firebase credentials file size: $(stat -c%s /var/task/firebase-adminsdk.json) bytes" && \
    python -c "import json; f=open('/var/task/firebase-adminsdk.json','r'); json.load(f); f.close(); print('Firebase credentials validated as valid JSON')"

# Create audio directory with proper permissions
RUN mkdir -p audio
RUN chmod 777 audio

# Set up entry point for AWS Lambda
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "lambda.handler" ]