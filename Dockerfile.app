
FROM python:3.13-alpine3.23
WORKDIR /usr/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 
ENV PYTHONPATH=/usr/backend
COPY entrypoint.sh .
RUN chmod a+x entrypoint.sh
COPY app/ ./app/

