#!/bin/sh
# wait-for-postgres.sh

set -ex  # Enable verbose output for debugging

host="$1"
shift

echo "Starting wait-for-postgres.sh script..."
echo "Host: $host"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"

# The 'until' loop will continue until the psql command succeeds.
# We use the environment variables that will be set in the docker-compose file.
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
echo "Starting uvicorn..."
exec /opt/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
