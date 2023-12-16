FROM python:3.11.1
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app
CMD ["python3", "main.py"]
