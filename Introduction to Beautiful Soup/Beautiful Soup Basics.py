from bs4 import BeautifulSoup
import requests

website = 'https://subslikescript.com/movie/Titanic-120338'
result = requests.get(website)
content = result.text

soup = BeautifulSoup(content, 'lxml')

box = soup.find('article', class_='main-article')
titel = soup.find('h1').get_text()

transcript = box.find('div', class_='full-script').get_text(strip=True, separator=' ')

with open(f'{titel}.txt', 'w') as file:  # titel + .txt
    file.write(transcript)
