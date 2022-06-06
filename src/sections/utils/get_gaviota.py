import requests
from bs4 import BeautifulSoup
from pathlib import Path


GAVIOTA_MAIN_URL = "https://tablebase.lichess.ovh/tables/standard/Gaviota/"

GAVIOTA_LOCAL_PATH = Path(__file__).parent.parent.parent.parent / "./data/gaviota/"
GAVIOTA_LOCAL_PATH.mkdir(parents=True, exist_ok=True)



r = requests.get(GAVIOTA_MAIN_URL)

for link in BeautifulSoup(r.text, "html.parser").find_all("a"):
    if link.attrs['href'] != '../':
        f = requests.get( GAVIOTA_MAIN_URL + link.attrs['href'])
        with open(GAVIOTA_LOCAL_PATH / link.attrs["href"], 'wb' ) as file:
            file.write(f.content)