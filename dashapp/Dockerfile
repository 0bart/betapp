FROM python:3.6-alpine

COPY . /

RUN pip install -r /requirements.txt

WORKDIR /app

EXPOSE 8050

CMD ["python", "./dashapp.py"]
