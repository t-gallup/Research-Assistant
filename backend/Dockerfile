FROM public.ecr.aws/lambda/python:3.11

# Download and build GLIBC 2.29
RUN wget http://ftp.gnu.org/gnu/libc/glibc-2.29.tar.gz && \
    tar -xvzf glibc-2.29.tar.gz && \
    cd glibc-2.29 && \
    mkdir build && cd build && \
    ../configure --prefix=/opt/glibc-2.29 && \
    make -j$(nproc) && \
    make install

# Set LD_LIBRARY_PATH to use the new GLIBC version
ENV LD_LIBRARY_PATH=/opt/glibc-2.29/lib:$LD_LIBRARY_PATH

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