# smtpcredtrap

Simple Python tool to listen on SMTP ports and capture authentication attempts.

During penetration tests, devices such as networked Multi Function Devices (MFDs) eg. printer/scanners are frequently compromised, often due to the default credentials not being changed by IT administrators. Some of these devices feature a "scan-to-email" function where an SMTP server can be configured so the scanner can send a scanned document via email to a recipient's email inbox.

The device's admin web UI will typically not display the stored SMTP password after it has been initially saved. To steal the plaintext password, the outgoing SMTP host could be changed from the legitimate server to a host controlled by the penetration tester. A fake SMTP service running on the tester's host could request authentication and capture the supplied SMTP credentials.

This tool can create fake SMTP services that capture credentials. Ensure your host is reachable (on the internal network or on an internet-exposed server) from the compromised device, then change its SMTP host to the hostname or IP address of the smtpcredtrap host and press the "test SMTP connection" button or wait for a user to use the "scan to email" function and the device should send the saved SMTP credentials for the legitimate SMTP service to this listener.

## Installation and Usage
1. Clone this repo
2. cd smtpcredtrap
3. The recommended way to install and run the tool is by using a Python virtual environment to avoid any dependency conflicts:
- install python3-virtualenv or python3-venv using pip or your operating system's package manager
- create a virtual environment by running python3 -m virtualenv .
- activate the virtual environment by running source bin/activate
- install the dependencies pip install -r requirements.txt
- ensure that no existing SMTP services are running on your host (eg. exim) and stop them if required
- run the tool (you will need to run as a privileged user to bind to SMTP ports): python3 main.py
- cd /home/kali/Documents/tools/smtpcredtrap

sudo openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -subj "/CN=smtp-test.local"

sudo chmod 600 key.pem
sudo ls -l cert.pem key.pem
- sudo "$PWD/venv/bin/python" "$PWD/main.py"
- force apps/services to authenticate with any stored SMTP credentials by changing the SMTP server to the IP of your host and wait for incoming authentication attempts
- plaintext credentials will be dumped to stdout
- Alternatively, install the dependencies pip install aiosmtpd if you don't want to create a virtual environment and run python3 main.py
- pentest-test@example.com
