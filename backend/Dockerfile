# Use Amazon Linux 2 as the base image (has newer GLIBC)
FROM amazonlinux:2 AS build

# Install Python 3.x and development tools
RUN yum update -y && \
    yum install -y python3 python3-pip python3-devel \
    gcc openssl-devel bzip2-devel libffi-devel wget tar gzip 

# Create app directory
WORKDIR /app

# Install AWS Lambda Runtime Interface Client
RUN pip3 install awslambdaric

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy function code
COPY *.py .
COPY firebase-adminsdk.json .

# Create audio directory with proper permissions
RUN mkdir -p audio
RUN chmod 777 audio

# Set up entry point
ENTRYPOINT [ "/usr/bin/python3", "-m", "awslambdaric" ]
CMD [ "lambda.handler" ]