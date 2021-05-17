import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

def get_page(url=None):
    """return HTML as string"""
    if url is None:
        raise Exception("URL cannot be None!")
    response = urllib.request.urlopen(url)
    if response.code != 200:
        raise Exception("Response code is not 200!")
    page = response.read().decode("UTF-8")
    return page


def get_bs_soup(page):
    soup = BeautifulSoup(page, 'html.parser')
    return soup


def print_elements_count(elements=None, timetable_instance=None, resource_name=None):
    """parameter timetable_instance should be "old" or "new"""
    t_count = len(elements)
    print(f"\n----There are {t_count} {resource_name} in {timetable_instance} Candle.---")


def print_first_characters(page=None):
    """print out first 300 characters of page"""
    print(page[:300])


def save_page_locally(page=None):
    if page is None:
        raise Exception("response_byte_object cannot be None!")
    with open('candle-saved-page.html', 'w') as f:
        f.write(page)