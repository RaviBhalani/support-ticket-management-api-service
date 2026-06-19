FROM ubuntu:latest
LABEL authors="ravib"

ENTRYPOINT ["top", "-b"]