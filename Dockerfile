# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app/src

# Copy the requirements.txt to install dependencies
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's source code
COPY ./src /app/src

# Expose the port Streamlit uses
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "src/app.py"]
