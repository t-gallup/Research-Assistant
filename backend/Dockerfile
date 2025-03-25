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

# Create audio directory with proper permissions
RUN mkdir -p audio
RUN chmod 777 audio

# Set up entry point for AWS Lambda
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "lambda.handler" ]