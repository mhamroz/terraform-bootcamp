FROM --platform=x86_64 alpine:latest
COPY requirements.txt .
RUN apk upgrade 
RUN apk --update add --no-cache python3 py3-pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD [ "python3", "app.py" ]
