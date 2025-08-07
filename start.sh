#!/bin/bash
# start.sh

set -e  # Exit on any error

echo "🚀 Starting application deployment..."

# Wait for database to be ready (optional but recommended)
echo "⏳ Waiting for database to be ready..."
python -c "
import time
import psycopg2
import os
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
if db_url:
    parsed = urlparse(db_url)
    for i in range(30):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:]
            )
            conn.close()
            print('Database is ready!')
            break
        except psycopg2.OperationalError:
            print(f'Database not ready, waiting... ({i+1}/30)')
            time.sleep(2)
    else:
        print('Database connection failed after 30 attempts')
        exit(1)
"

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi

# Start the application
echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
