# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

HEALTHCHECK CMD curl --fail http://localhost:8080 || exit 1

COPY test/TRUPPE-CAMMELLATE.jpg /tmp/TRUPPE-CAMMELLATE.jpg
COPY ../tools/ ../tools/
# COPY prompts/ prompts/
COPY ../utils/ ../utils/
COPY gpto_agent.py gpto_agent.py 

#for normal deploy
ENTRYPOINT ["python", "gpto_agent.py"]

