FROM python:3.6-alpine

WORKDIR /usr/src/app

# Bundle app source
COPY . .

RUN python setup.py install
RUN pip install falcon-jsonify
EXPOSE 8010

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/usr/src/app/gunicorn.py", "chariot_privacy_engine.app:app"]
