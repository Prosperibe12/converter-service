ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install os dependencies for our mini vm
RUN apt-get update \ 
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    ffmpeg \
    && pip install --no-cache-dir --upgrade pip

# Set the working directory to that same code directory
WORKDIR /app

# Copy the requirements file into the container
COPY ./requirements.txt /app

# Install the Python project requirements
RUN pip install --no-cache-dir -r /app/requirements.txt 

# Copy the rest of the code
COPY . /app

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Run the Flask project via the runtime script
# when the container starts
CMD ["python3", "consumer.py"]