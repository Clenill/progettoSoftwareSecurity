
FROM python:3.13-alpine
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/usr
ARG APP_PORT
COPY app .
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $APP_PORT"]

