from bs4 import BeautifulSoup
import requests

root = 'https://subslikescript.com'
website = f'{root}/movies'
result = requests.get(website)
content = result.text

soup = BeautifulSoup(content, 'lxml')

box = soup.find('article', class_='main-article')
links = []
for link in box.find_all('a', href=True):
    links.append(link['href'])

print(links)
titels = []
for link in links:
    website = f'{root}/{link}'
    result = requests.get(website)
    content = result.text

    soup = BeautifulSoup(content, 'lxml')

    box = soup.find('article', class_='main-article')
    titel = soup.find('h1').get_text()
    titels.append(titel)

print(titels)