FROM python:3.11-slim

# system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# set working dir
WORKDIR /app

# copy files
COPY . .

# install deps
RUN pip install --no-cache-dir -r requirements.txt

# expose API port
EXPOSE 8000

# run server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
