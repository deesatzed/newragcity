FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl build-essential postgresql-client libgomp1 && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/root/.local/bin:/root/.cargo/bin:$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Copy project files from backend context
COPY . .

RUN uv venv --python /usr/local/bin/python3.13 $VIRTUAL_ENV
RUN . $VIRTUAL_ENV/bin/activate && uv pip install -e .

RUN chmod +x ./wait-for-postgres.sh

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
