# Use Python 3.11 image with a newer Linux base
FROM public.ecr.aws/lambda/python:3.11

# Install AWS Lambda Runtime Interface Client
RUN pip install --no-cache-dir awslambdaric

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY *.py ${LAMBDA_TASK_ROOT}/

# Create audio directory with proper permissions
RUN mkdir -p ${LAMBDA_TASK_ROOT}/audio
RUN chmod 777 ${LAMBDA_TASK_ROOT}/audio

# Set up CMD for AWS Lambda
CMD [ "lambda.handler" ]