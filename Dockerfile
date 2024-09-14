# Parent image used
FROM python:3.9-slim-buster

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt

# Bundle app source
COPY ./app ./app

# Command to start application
CMD ["python", "./app/app.py"]
