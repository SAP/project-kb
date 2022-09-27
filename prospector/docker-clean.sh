#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
DONE="[${GREEN}DONE${NC}]"
PROGRESS="[${YELLOW}....${NC}]"

echo -ne "${PROGRESS} Stop all running containers\r"
docker stop "$(docker ps -q)" 2>/dev/null
echo -ne "${DONE} Stop all running containers\r"
echo -ne '\n'

echo -ne "${PROGRESS} Removing all stopped containers\r"
docker container prune -y 2>/dev/null
echo -ne "${DONE} Removing all stopped containers\r"
echo -ne '\n'

echo -ne "${PROGRESS} Remove all images\r"
docker rmi "$(docker images -q)" 2>/dev/null
echo -ne "${DONE} Remove all images\r"
echo -ne '\n'

echo -ne "${PROGRESS} Cleaning volumes\r"
docker volume rm "$(docker volume ls -q)" 2>/dev/null
echo -ne "${DONE} Cleaning volumes\r"
echo -ne "\n"

echo -ne "${PROGRESS} Cleaning all\r"
docker system prune -a -y 2>/dev/null
echo -ne "${DONE} Cleaning what's left\r"
echo -ne "\n"