#!/usr/bin/env bash
echo "Starting ollama server..."
ollama serve &

while [[ "$(ollama list | grep NAME)" == "" ]]; do
	sleep 1
done

ollama pull qwen2.5:0.5b
