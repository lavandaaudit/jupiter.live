import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
from datetime import datetime

data = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "junocam": {"perijove": "Unknown", "images": []},
    "dsn": {"status": "неактивний", "data_rate": "N/A", "frequency": "N/A", "rtt": "N/A"},
    "radio_jove": {"stream_url": "https://www.youtube.com/embed/live_stream?channel=UCtawz3MnMBwjz9ShhSC0ygQ&autoplay=1"}
}

# JunoCam — останній Perijove та знімки
try:
    url = "https://www.missionjuno.swri.edu/junocam/processing"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Шукаємо останній Perijove (заголовки або посилання)
    perijove_header = soup.find('h2', string=lambda t: t and 'Perijove' in t)
    if perijove_header:
        data['junocam']['perijove'] = perijove_header.text.strip()
    
    # Останні 5 raw images
    images = soup.find_all('img', src=lambda s: s and 'junocam' in s.lower())
    img_urls = ["https://www.missionjuno.swri.edu" + img['src'] for img in images[:5] if img.get('src')]
    data['junocam']['images'] = img_urls or ["https://science.nasa.gov/wp-content/uploads/2023/09/jupiter_marble_1024.jpg"]
except Exception as e:
    print(f"JunoCam error: {e}")

# DSN статус для JUNO
try:
    dsn_url = "https://eyes.nasa.gov/dsn/data/dsn.xml"
    response = requests.get(dsn_url, timeout=10)
    root = ET.fromstring(response.content)
    
    for dish in root.findall('dish'):
        target = dish.find('target')
        if target is not None and target.get('name') == 'JUNO':
            data['dsn']['status'] = "активний"
            down = dish.find('.//downSignal[@active="true"]')
            if down is not None:
                data['dsn']['data_rate'] = down.get('dataRate', 'N/A')
                data['dsn']['frequency'] = down.get('frequency', 'N/A')
            data['dsn']['rtt'] = target.get('rtlt', 'N/A')
            break
except Exception as e:
    print(f"DSN error: {e}")

# Записуємо JSON
with open('jupiter_state.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("jupiter_state.json оновлено!")
