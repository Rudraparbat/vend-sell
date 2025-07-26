# Use slim image for a smaller footprint
FROM python:3.13.2-slim-bookworm


# Set the working directory inside the container
WORKDIR /app

# Copy the rest of the application
COPY . .

RUN pip install --no-cache-dir -r requirements.txt  


# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]