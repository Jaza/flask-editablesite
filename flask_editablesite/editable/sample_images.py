from bs4 import BeautifulSoup
import requests


def scrape_sample_images(url, parentelname=None, parentelclass=None, onlyfirstel=False):
    """Scrapes the given URL for sample image links."""

    r  = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    hrefs = []

    if parentelname:
        soup_kwargs = {}

        if parentelclass:
            soup_kwargs['class_'] = parentelclass

        for parent_el in soup.find_all(parentelname, **soup_kwargs):
            if onlyfirstel:
                link = next(iter(parent_el.find_all('a'))).get('href')
                hrefs.append(link)
            else:
                for link in parent_el.find_all('a'):
                    hrefs.append(link.get('href'))
    else:
        for link in soup.find_all('a'):
            hrefs.append(link.get('href'))

    return hrefs
