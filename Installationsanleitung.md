## Linux 🐧

1. Python 3.10+ installieren
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

2. Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

3. Abhängigkeiten installieren
pip install discord.py requests psutil python-dotenv GPUtil

4. Bot starten
python3 rusty.py


## Raspberry Pi OS

1. System aktualisieren
sudo apt update && sudo apt upgrade -y

2. Python 3.10+ installieren
sudo apt install -y python3 python3-pip python3-venv
python3 --version

3. Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

4. Abhängigkeiten installieren
pip install discord.py requests psutil python-dotenv GPUtil
⚠️ GPUtil findet auf dem Pi keine GPU, das ist okay.

5. Bot starten
python3 rusty.py


## Windows 

1. Python 3.10+ installieren
Gehe zu python.org/downloads
Neueste Version herunterladen und installieren

2. Virtuelle Umgebung erstellen
python -m venv venv
venv\Scripts\activate

3. Abhängigkeiten installieren
pip install discord.py requests psutil python-dotenv GPUtil

4. Bot starten
python rusty.py
