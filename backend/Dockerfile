FROM public.ecr.aws/lambda/python:3.11

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY *.py ${LAMBDA_TASK_ROOT}
COPY firebase-adminsdk.json ${LAMBDA_TASK_ROOT}

# Create directories
RUN mkdir -p ${LAMBDA_TASK_ROOT}/audio
RUN chmod 777 ${LAMBDA_TASK_ROOT}/audio

# Set the CMD to your handler
CMD [ "lambda.handler" ]