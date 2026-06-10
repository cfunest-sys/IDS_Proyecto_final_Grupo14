FROM python:3.11-slim 

WORKDIR /app/frontend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_frontend/ .

EXPOSE 8080

CMD ["python","app.py"]

