import requests
import re
import product
from bs4 import BeautifulSoup
import bs4

#does this string contain amount, eg "Ca 200g", or not, eg "Klass 1"
def is_amount(amount_str: str) -> bool:
    #TODO: implement
    return True

#remove surrounding whitespace and empty elements
def remove_whitespace_elements(original: list[str]) -> list[str]:
    return [el.strip() for el in original if len(el.strip()) != 0]

def filter_price_string(price_string: str) -> str:
    return re.sub(r'[^\d.,]*', '', price_string.strip())

# wrapper around http request to prevent errors
def safe_request(http_str: str) -> bytes:
    try:
        r = requests.get(http_str)
        return r.content
    except requests.exceptions.ConnectionError:
        return bytes()

# None -> "", other -> other.strip()
def safe_none_str(maybe_string: None | str) -> str:
    if maybe_string == None:
        return ""
    else:
        return maybe_string.strip()

# get string safetly
def soup_safe_str(maybe_soup: BeautifulSoup | bs4.Tag | bs4.NavigableString | None) -> str:
    if maybe_soup == None:
        #assert False
        return ""
    elif isinstance(maybe_soup, bs4.NavigableString):
        return safe_none_str(maybe_soup)
    return safe_none_str(maybe_soup.string)

def soup_find(soup: BeautifulSoup, kind: str, class_tag: str) -> bs4.Tag | bs4.NavigableString | None:
    return soup.find(kind, class_=class_tag)

# make request from http address and return soup object
def address_to_soup(address: str) -> BeautifulSoup:
    content: bytes = safe_request(address)
    return BeautifulSoup(content, 'html.parser')

# Parse lidl offers from html
def lidl_parse(soup: BeautifulSoup) -> list[product.Product]:
    s: list[BeautifulSoup] = soup.find_all('div', class_ = "nuc-a-flex-item nuc-a-flex-item--width-6 nuc-a-flex-item--width-4@sm")
    product_list: list[product.Product] = []
    for el in s:
        #TODO: Image link
        product_price_el = el.find('span', class_ = "lidl-m-pricebox__price")
        product_name_el = el.find('h3', class_ = "ret-o-card__headline")
        price_str: str = filter_price_string(soup_safe_str(product_price_el))
        name_str: str = soup_safe_str(product_name_el)
        product_list.append(product.Product(
            name=name_str, 
            price=price_str, 
            store=product.Store.LIDL))
    return product_list

#<div class="ItemTeaser-content">
#<div class="Grid-cell u-size1of2 u-xsm-size1of2 u-md-size1of4 u-lg-size1of6 js-drOffer js-offerItem" data-eag-id="12960" data-store-id="165420">
#<article class="ItemTeaser" itemscope="" itemtype="http://schema.org/Product">
def coop_parse(soup: BeautifulSoup) -> list[product.Product]:
    s = soup.find_all('article', class_ = "ItemTeaser")
    product_list: list[product.Product] = []
    for el in s:
        #['3 för', '79:-']
        #['50%', 'rabatt']
        #['49', '90', '/st']
        price_raw: str = " ".join(remove_whitespace_elements(list(el.find('span', class_ = "Splash-content").strings)))
        heading: str = el.find('h3', class_ = "ItemTeaser-heading").string
        description: str = " ".join(remove_whitespace_elements(list(el.find('p', class_ = "ItemTeaser-description").strings)));
        #print("image link:", el.find('img', class_ = "u-posAbsoluteCenter").get('src'))
        #print("price:", price_raw)
        #print("heading:", heading)
        #print("description:", description)
        #print()
        product_list.append(product.Product(
            name=heading, 
            price=price_raw, 
            store=product.Store.COOP,
            description=description))
    return product_list

def ica_parse(soup: BeautifulSoup) -> list[product.Product]:
    #<section class="offer-category details open">
    offer_groups: list[BeautifulSoup] = soup.find_all('section', class_ = "offer-category details open")
    product_list: list[product.Product] = []
    for offer_group in offer_groups:
        header_soup = offer_group.find('header', class_ = "offer-category__header summary active")
        category: str = soup_safe_str(header_soup)
        offers = offer_group.find_all('div', class_="offer-category__item")
        print("category:", category, "offers:", len(offers))
        for offer in offers:
            title: str = soup_safe_str(offer.find('h2', class_="offer-type__product-name splash-bg icon-store-pseudo"))
            description: str = soup_safe_str(offer.find('p', class_="offer-type__product-info"))
            price: str = soup_safe_str(offer.find('div', class_="product-price__price-value"))\
            + " " +      soup_safe_str(offer.find('div', class_="product-price__decimal"))\
            + " " +      soup_safe_str(offer.find('div', class_="product-price__unit-item benefit-more-info"))
            price = price.strip()
            #print(offer.prettify())
            #exit()

            print("    title:", title)
            print("    description:", description)
            print("    price:", price)
            product_list.append(product.Product(
                name=title, 
                price=price, 
                store=product.Store.ICA,
                description=description,
                category=category))

    return product_list

soup = address_to_soup('https://www.ica.se/butiker/maxi/orebro/maxi-ica-stormarknad-universitetet-orebro-15088/erbjudanden/')
print(ica_parse(soup))
#soup = address_to_soup('https://www.coop.se/butiker-erbjudanden/coop/coop-kronoparken/')
#print(coop_parse(soup))
#soup = address_to_soup('https://www.lidl.se/veckans-erbjudanden')
#print(lidl_parse(soup))

