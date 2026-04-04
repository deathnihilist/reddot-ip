# REDDOT IP
**Advanced Origin IP Discovery & Infrastructure Analysis Framework** *Developed by: [Deathnihilist](https://github.com/deathnihilist)*

---

## Description
REDDOT IP is a specialized reconnaissance framework engineered for security researchers and penetration testers operating within Linux environments. Its primary objective is to identify the Origin IP (backend server) of targets shielded by Web Application Firewalls (WAF) or Reverse Proxies such as Cloudflare, Akamai, and Sucuri.

The tool automates the process of footprinting SSL certificate metadata and historical DNS records. By cross-referencing data from global scanning engines, REDDOT IP uncovers misconfigurations that leave a server’s real IP address exposed to the public internet, effectively bypassing the proxy layer.



## Core Technical Features
1. Multi-Engine Intelligence: Integrated with Shodan and Censys APIs to correlate global infrastructure data.
2. SSL/TLS Footprinting: Advanced matching logic that tracks unique certificate serial numbers and fingerprints across the IPv4 space.
3. WAF Bypass Logic: Identifies direct-to-ip communication channels that bypass CDN edge nodes.
4. Infrastructure Analysis: Detects whether a target is hosted on dedicated hardware or shared hosting environments.
5. Git LFS Integration: Includes an extensive pre-configured payload database (200MB+) managed via Git Large File Storage for high-efficiency fuzzing.
6. Automated Session Logging: All reconnaissance data is structured and exported to the logs/ directory for post-operational reporting.
7. Modular Architecture: Built with a flexible core to allow for rapid integration of new vulnerability scanning modules.

## Installation and Setup

REDDOT IP is optimized for Kali Linux. Follow the sequence below to initialize the environment:
1. Install Git LFS (Required for Payloads)
Since the framework includes large wordlists, Git LFS must be initialized on your system before cloning:
sudo apt update && sudo apt install git-lfs -y
git lfs install

2. Clone and Initialize
a. git clone https://github.com/deathnihilist/reddot-ip.git
b. cd reddot-ip
c. chmod +x setup.sh
d.  ./setup.sh

## Usage
To launch the primary interface:
python3 reddot.py


## Development Roadmap
REDDOT IP is under active development. The framework is designed to be a living project, with frequent updates planned for the following areas:
1. Integration of additional OSINT scanning engines (BinaryEdge, Zoomeye).
2. Expansion of the vultuner module for automated vulnerability assessment.
3. Enhanced bypass techniques for evolving WAF security postures.
4. Customizable threading logic for high-performance scanning.

## New modules and logic updates will be pushed regularly to the main branch. Users are encouraged to run git pull frequently to ensure they are using the latest tactical capabilities.

## Disclaimer
This tool is intended for authorized security auditing and educational purposes only. Unauthorized access to computer systems is illegal. The developer assumes no liability for any misuse or damage caused by this program.
