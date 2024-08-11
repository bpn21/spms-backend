FROM python:3.9-alpine

WORKDIR /app/

# You should include apk commands in your Dockerfile when your Python application has dependencies on system libraries or tools that are not included in the base Python image. These dependencies are typically required for certain Python packages with C extensions or for the correct functioning of your application.

# Here's an example scenario:

# Let's say your Python application uses the PostgreSQL database, and you are using a Python package like psycopg2 as a database adapter. psycopg2 has some system-level dependencies, and you need to ensure those dependencies are present in your Docker image.

RUN apk update \
    && apk add --no-cache \
    tzdata make \
    gcc g++ musl-dev libffi-dev openssl-dev \
    curl cargo \
    python3-dev jpeg-dev zlib-dev rust \
    postgresql-dev

# Copy the rest of your application code into the container
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

ENV TZ Asia/Kathmandu

# CMD ["ls", "-la", "/app"]
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]
# CMD ["manage.py","runserver","0.0.0.0:8000"]