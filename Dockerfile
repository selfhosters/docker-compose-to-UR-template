FROM python:3.7-alpine3.10

LABEL maintainer="Roxedus"\ state="WIP"

COPY / /app

RUN python3 -m pip install -r /app/requirements.txt

WORKDIR /app/

ENTRYPOINT ["python3", "/app/CLI.py"]
CMD ["-a"]