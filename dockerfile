# Use a base image with Python support
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy main.py, config.json, and requirements.txt files to the working directory in the container
COPY main.py .
COPY config.json .
COPY requirements.txt .

# Install necessary dependencies for your application from the requirements.txt file
RUN pip install -r requirements.txt

# Expose port 8000 to make it accessible from outside the container
EXPOSE 8000

# Command to run uvicorn with main.py as the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]