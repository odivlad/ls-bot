FROM fedora:40

RUN dnf install python3.11 poetry -y && \
    rm -rf /var/cache/dnf/*

WORKDIR /app

COPY . .

RUN poetry env use 3.11 && poetry install

CMD ["poetry", "run", "ls-bot"]
