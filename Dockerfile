# Pull base image
FROM python:3.9-slim

# Upgrade pip
RUN pip install --upgrade pip

# Set work directory
WORKDIR /social_network_flask

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Expose port 4000
EXPOSE 4000

# Set command to run when the container starts
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]