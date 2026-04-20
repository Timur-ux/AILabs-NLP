FROM ollama/ollama

COPY ./ollama/* /tmp/
RUN /tmp/serveAndPull.sh

