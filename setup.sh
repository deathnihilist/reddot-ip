#!/bin/bash

echo -e "\e[31m[!] Setting up REDDOT IP by Deathnihilist...\e[0m"
sleep 1

# Update package list
sudo apt-get update

# Install python3 and pip if not exists
sudo apt-get install -y python3 python3-pip

# Install requirements
pip3 install -r requirements.txt

# Give execution permission to the main file
chmod +x reddot.py

echo -e "\e[32m[+] Setup Complete! Run it with: python3 reddot.py\e[0m"