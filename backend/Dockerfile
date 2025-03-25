FROM public.ecr.aws/lambda/python:3.11

# Install necessary system libraries for azure speech SDK
RUN yum update -y && \
    yum install -y wget tar gzip && \
    yum clean all

# Copy function code to the Lambda task root directory
COPY *.py ${LAMBDA_TASK_ROOT}/

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create audio directory with proper permissions
RUN mkdir -p ${LAMBDA_TASK_ROOT}/audio
RUN chmod 777 ${LAMBDA_TASK_ROOT}/audio

# The CMD specifies the handler
CMD [ "lambda.handler" ]