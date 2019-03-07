FROM python:3.6-alpine

WORKDIR /usr/src/app

# Bundle app source
COPY . .

RUN apk add git gnupg gcc g++ make python3-dev libffi-dev openssl-dev gmp-dev && pip install pytest && python setup.py install
RUN cd iot-modeling-language && python setup.py install && cd ..

CMD ["python", "./chariot_privacy_engine/app.py"]