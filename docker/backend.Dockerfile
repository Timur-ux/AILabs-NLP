FROM ubuntu:22.04

RUN apt update 
RUN apt install -y python3 python3-venv
RUN useradd -u 1000 -m api
USER api
COPY --chown=api:api ./server/requirements.txt /home/api/app/requirements.txt

WORKDIR /home/api/app
RUN python3 -m venv venv
RUN ./venv/bin/pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=api:api ./server /home/api/app
EXPOSE 8000
ENTRYPOINT [ "./venv/bin/fastapi", "run" ]

