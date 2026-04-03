# REDDOT IP 🔴
**Advanced Origin IP Finder & WAF Bypass Tactical Tool** *Developed by: [Deathnihilist](https://github.com/deathnihilist)*

---

## 🛠 Description
**REDDOT IP** is a tactical reconnaissance tool built for **Kali Linux** environments. Its primary mission is to strip away the "mask" provided by WAFs (Web Application Firewalls) like Cloudflare, Akamai, or Sucuri to reveal the **Origin IP** (the real backend server address).

By leveraging deep metadata from **Shodan** and **Censys**, REDDOT IP tracks SSL certificate footprints and DNS misconfigurations that often leave the real server exposed to the public web.



## 🔥 Features
- ⚡ **Dual-Engine Intelligence**: Simultaneous integration with Shodan and Censys APIs for maximum coverage.
- 🛡️ **WAF/Cloudflare Bypass**: Intelligent SSL Certificate matching logic to find IPs behind the proxy.
- 🏘️ **Shared Hosting Detection**: Analyzes if the target is on a crowded infrastructure or a dedicated server.
- 📝 **Tactical Auto-Logging**: All discoveries are automatically saved in the `logs/` directory for post-op analysis.
- 🎨 **Modern Terminal UI**: Clean, aggressive ASCII art interface with color-coded status updates.

## 🚀 Installation

Ensure you are running **Kali Linux**, then execute the following commands:

```bash
# Clone the repository
git clone [https://github.com/deathnihilist/reddot-ip.git](https://github.com/deathnihilist/reddot-ip.git)

# Enter the directory
cd reddot-ip

# Run the automated setup script
chmod +x setup.sh
./setup.sh