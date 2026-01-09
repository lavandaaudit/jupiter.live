# scraper.py

import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Function to scrape JunoCam latest images
def get_junocam_data():
    url = "https://www.missionjuno.swri.edu/junocam/processing"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the latest Perijove section (adapt based on actual HTML structure)
        # This is an example; inspect the page for accurate selectors
        latest_section = soup.find('div', class_='perijove-latest')  # Hypothetical class
        if latest_section:
            perijove = latest_section.find('h2').text.strip() if latest_section.find('h2') else 'Unknown'
            images = [img['src'] for img in latest_section.find_all('img', class_='junocam-image')][:5]
        else:
            perijove = 'Unknown'
            images = []
        
        return {'perijove': perijove, 'images': images}
    except Exception as e:
        print(f"Error scraping JunoCam: {e}")
        return {'perijove': 'Error', 'images': []}

# Function to get DSN Now data for JUNO
def get_dsn_data():
    url = "https://eyes.nasa.gov/dsn/data/dsn.xml"
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        juno_data = {}
        for dish in root.findall('dish'):
            target = dish.find('target')
            if target is not None and target.text == 'JUNO':
                down_signal = dish.find('downSignal')
                if down_signal:
                    data_rate = down_signal.find('dataRate').text if down_signal.find('dataRate') else 'N/A'
                    frequency = down_signal.find('frequency').text if down_signal.find('frequency') else 'N/A'
                    rtt = dish.find('roundTripLightTime').text if dish.find('roundTripLightTime') else 'N/A'
                    juno_data = {
                        'data_rate': data_rate,
                        'frequency': frequency,
                        'rtt': rtt
                    }
                break
        return juno_data
    except Exception as e:
        print(f"Error scraping DSN: {e}")
        return {}

# Function to get Radio JOVE data (example; adapt to actual API or feed)
def get_radio_jove_data():
    # Placeholder: Use actual Radio JOVE API or RSS if available
    # For example, fetch latest spectrogram URL
    url = "https://radiojove.gsfc.nasa.gov/data/archive/latest_spectrogram.json"  # Hypothetical
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {'intensity_graph_url': data.get('url', 'N/A'), 'latest_burst': data.get('burst', 'None')}
    except Exception:
        return {'intensity_graph_url': 'N/A', 'latest_burst': 'None'}

# Main function
def main():
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'junocam': get_junocam_data(),
        'dsn': get_dsn_data(),
        'radio_jove': get_radio_jove_data(),
        # Add more: Magnetosphere, etc., using similar methods
    }
    
    with open('jupiter_state.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()
