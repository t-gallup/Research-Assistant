# Use Amazon Linux 2 as the base image (has newer GLIBC)
FROM amazonlinux:2 AS build

# Install Python 3.11 and development tools
RUN yum update -y && \
    yum install -y python3.11 python3.11-pip python3.11-devel \
    gcc openssl-devel bzip2-devel libffi-devel wget tar gzip 

# Create app directory
WORKDIR /app

# Install AWS Lambda Runtime Interface Client
RUN pip3.11 install awslambdaric

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip3.11 install -r requirements.txt

# Copy function code
COPY *.py .
COPY firebase-adminsdk.json .

# Create audio directory with proper permissions
RUN mkdir -p audio
RUN chmod 777 audio

# Set up entry point
ENTRYPOINT [ "/usr/local/bin/python3.11", "-m", "awslambdaric" ]
CMD [ "lambda.handler" ]