FROM registry.gitlab.com/chariot-h2020/chariot_base:latest AS builder

WORKDIR /workspace
COPY . .
RUN apk add gnupg gcc g++ make python3-dev libffi-dev openssl-dev gmp-dev
RUN pip install -U pip && pip install -r requirements_dev.txt && pip install pytest && pip install gunicorn
RUN python setup.py install

RUN pip uninstall pycrypto -y
RUN pip install pycryptodome -y --force-reinstall

FROM python:3.7-alpine AS final
WORKDIR /workspace
COPY --from=builder /usr/local/lib/python3.7 /usr/local/lib/python3.7
RUN apk add libffi-dev openssl-dev gmp-dev

CMD ["python3", "-m", "chariot_privacy_engine.app"]
