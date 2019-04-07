FROM alpine:3.7

COPY . /

RUN apk add --no-cache python3-dev build-base linux-headers pcre-dev python3
RUN pip3 install --no-cache-dir -r /requirements.txt

EXPOSE 4000

CMD [ "uwsgi", "--ini", "uwsgi.ini"]
