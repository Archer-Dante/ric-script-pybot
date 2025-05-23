# FROM python:3.12
# WORKDIR /app
# COPY . /app
# RUN pip install -r requirements.txt
# CMD ["python", "main.py"]


FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]


# docker build -t ric_bot .