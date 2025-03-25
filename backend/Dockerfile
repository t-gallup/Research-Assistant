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

# Set environment variables for Lambda
ENV PYTHONPATH=/var/task

# Use the Lambda Runtime Interface Emulator as the entrypoint
# COPY lambda-entrypoint.sh /
# RUN chmod +x /lambda-entrypoint.sh
# ENTRYPOINT ["/lambda-entrypoint.sh"]

# # Specify the handler
# CMD ["lambda.handler"]

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

# Set environment variables for Lambda
ENV PYTHONPATH=/var/task

# Use a shell form ENTRYPOINT to avoid quoting issues
ENTRYPOINT python -m awslambdaric lambda.handler