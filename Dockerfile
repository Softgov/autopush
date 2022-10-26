FROM python:latest

ARG USERNAME=user

RUN useradd -ms /bin/bash ${USERNAME} || (addgroup ${USERNAME} && adduser ${USERNAME} -D -G ${USERNAME})

RUN which git || ((apt-get -yq update && apt-get -yq install git && rm -rf /var/lib/apt/lists/*) || (apk update --no-cache && apk add --no-cache git))

USER ${USERNAME}

WORKDIR /app

COPY --chown=${USERNAME}:${USERNAME} ./requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=${USERNAME}:${USERNAME} . .

ENTRYPOINT ["python", "main.py"]
