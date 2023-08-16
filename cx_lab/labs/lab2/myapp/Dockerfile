FROM ubuntu:latest
WORKDIR /app
COPY requirements.txt .
RUN apt update
RUN apt install python3 python3-pip -y
RUN pip install -r requirements.txt
COPY . .
CMD [ "python3", "./app.py" ]