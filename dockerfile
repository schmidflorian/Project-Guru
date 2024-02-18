FROM python:3.9-slim

ENV HOST=0.0.0.0

ENV LISTEN_PORT 8080

EXPOSE 8080

RUN apt-get update && apt-get install -y git

# Set the working directory inside the container
WORKDIR /app

# First, copy only the requirements.txt file and install Python dependencies
# This leverages Docker's cache to avoid reinstalling dependencies if they haven't changed
COPY requirements.txt .
RUN pip install --upgrade --no-cache-dir -r requirements.txt

# Now copy the rest of your application's code into the container
COPY . .

CMD ["streamlit", "run", "main.py", "--server.port", "8080"]