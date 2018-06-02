import requests
import re
import random
import time
import csv
import urllib
import os
from bs4 import BeautifulSoup as Bs
from requests import exceptions as req_exceptions
from collections import Counter
import threading
import sys

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# API Handler for Amazon
# amazon = Amazon('AKIAJWDZJTS6Z7MSPIHA', 'ikIQ07StRN7lQvyo/oRcV8cSrU8NpOINxLVm61VT', 'jesusp0b-20')

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# TODO (1) Items that don't have any price (unavailable)


def get_proxies():
    """Usage:
        Returns a list of dictionary pair values of http/https proxies to use compatible with python's request proxy format
        Param: None
        Return type: List (dictionaries)"""
    _proxies = []
    proxy_sites = ['https://www.us-proxy.org/', 'https://www.sslproxies.org/', 'https://free-proxy-list.net/', 'https://free-proxy-list.net/anonymous-proxy.html', 'https://free-proxy-list.net/uk-proxy.html']
    for site in proxy_sites:
        table_bs = Bs(requests.get(site).text, 'html.parser').find('table', {'id': 'proxylisttable'})
        for row in table_bs.find_all('tr'):
            try:
                row_data = [column.text for column in row.find_all('td')]
                if row_data[4].lower() != 'transparent' and row_data[6].lower() == 'yes':
                    _proxies.append((row_data[0], row_data[1]))
            except IndexError:
                    continue
    random.shuffle(_proxies)
    return _proxies

proxies = iter(get_proxies())
curr_proxy = {}
AMZ_URL = "https://www.amazon.com"
path = os.getcwd() + '\\Results'
thread_pool = []
if 'Results' not in os.listdir(os.getcwd()):
    os.mkdir(os.getcwd() + '\\Results')


def rnd_user_agent():
    """Returns a random user agent"""
    return {'User-Agent': random.choice(['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
                                         'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30 ChromePlus/1.6.3.1',
                                         'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
                                         'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
                                         'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
                                         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
                                         'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; pl-PL; rv:1.0.1) Gecko/20021111 Chimera/0.6',
                                         'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; Browzar)',
                                         'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30 ChromePlus/1.6.3.1',
                                         'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.98 Safari/534.13 ChromePlus/1.6.0.0',
                                         'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.215 Safari/534.10 ChromePlus/1.5.1.1',
                                         'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.215 Safari/534.10 ChromePlus/1.5.1.1',
                                         'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7 ChromePlus/1.5.0.0',
                                         'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))',
                                         'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; yie8)',
                                         'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)',
                                         'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
                                         'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
                                         'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 7.0; InfoPath.3; .NET CLR 3.1.40767; Trident/6.0; en-IN)',
                                         'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))',
                                         'Mozilla/5.0 (Windows NT 6.2; rv:22.0) Gecko/20130405 Firefox/22.0',
                                         'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
                                         'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
                                         'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0',
                                         'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0'])}


def force_next_proxy():
    """Assigns next proxy to curr_proxy variable, forces to try a .next() call on proxies iterator.
       If StopIteration raised, fetch a new list of proxies and yield the first one from it
       Param: none
       Return type: dict"""
    global proxies, curr_proxy
    try:
        curr_proxy = proxies.next()
        print curr_proxy
        return curr_proxy
    except StopIteration:
        proxies = iter(get_proxies())
        return force_next_proxy()


def connect_obj(url):
    """Returns a requests object connection to string @url via the current proxy in use. checks for timeouts & bad proxies.
       Param: url (string)
       Return type: requests get object"""
    global curr_proxy
    try:
        connection = requests.get(url, proxies=curr_proxy, timeout=30, headers=rnd_user_agent())
        if connection.elapsed.seconds >= 10:
            print "Successful get request, however proxy took too long, switching..."
            curr_proxy = proxies.next()
        return connection

    # Bad proxies & Connections try blocks.
    except req_exceptions.ConnectionError, err:
        print err.message, err.response
        curr_proxy = force_next_proxy()
        return connect_obj(url)
    except req_exceptions.ChunkedEncodingError, err:
        print err.message, err.response
        curr_proxy = force_next_proxy()
        return connect_obj(url)
    except req_exceptions.ReadTimeout, err:
        print err.message, err.response
        curr_proxy = force_next_proxy()
        return connect_obj(url)
    except req_exceptions.MissingSchema, err:
        print err.message, err.response
    except AttributeError, err:
        print err.message
        curr_proxy = force_next_proxy()
        return requests.get(url, timeout=30, headers=rnd_user_agent())


def legit_bs(url):
    """Returns a verified beautifulSoup object (Skips Captcha) - checks for bot detection captcha and uses a different proxy to generate it if caught
       Param: url (string), chunk (string)
       Return type: BeautifulSoup object OR False (boolean) if the no offer page is found"""
    global curr_proxy
    bs = connect_obj(url)
    chunk = bs.text
    bs = Bs(chunk, 'html.parser')
    try:
        if 'robot check' in bs.title.text.lower():
            curr_proxy = force_next_proxy()
            return legit_bs(url)
    except AttributeError:
        return bs('<Title> Im a mistake! </Title>', 'html.parser')
    return bs


def build_url(keywords):
    """Builds the search url for given keywords
       Param: keywords (string)
       Return type: string"""
    root_url = 'https://www.amazon.com/s/?url=field-keywords='

    encoded_kws = urllib.quote(keywords)

    return root_url + encoded_kws


class AmzPage:
    def __init__(self, keywords):
        self.url = build_url(keywords)
        self.top_ten_words = []
        self.products = []
        self.search_value = keywords
        self.errors = list()
        self.parse_page(self.url)
        self.get_top_words()

    def parse_page(self, url):
        """Accepts a url to parse using beautiful soup to extract urls and fill self.products with ProductPage objects
           Param: url (string)
           Return type: None"""
        bs = legit_bs(url)

        products = bs.find_all(attrs={"data-asin": True})
        for product_bs in products:
            if products.index(product_bs) > 19:
                return
            if not product_bs.find("h5"):
                asin = product_bs['data-asin']
                url = 'https://www.amazon.com/dp/' + asin
                time.sleep(random.uniform(1.0, 1.5))
                product_page = ProductPage(url)
                if product_page.valid:
                    self.products.append(product_page)
                    if product_page.errors:
                        self.errors.append((url, product_page.errors))

    def get_top_words(self):
        """Iterates over all the found product's titles, assigning the top 10 words to self.top_ten_words
            Param: None
            Return type: None"""
        words = Counter()
        for product in self.products:
            title = product.title.split(" ")
            for word in title:
                words[word] += 1

        self.top_ten_words = words.most_common(10)

    def to_csv(self):
        return {'url': self.url.encode('utf-8'), 'keywords': self.search_value, 'top_words': self.top_ten_words}

    def over_800_revs(self):
        """Returns all the products that have over 800 reviews
           Param: None
           Return type: list (ProductPage)"""
        return [product for product in self.products if product.reviews >= 800]

    def under_100_revs(self):
        """Returns all the products that have over 800 reviews
           Param: None
           Return type: list (ProductPage)"""
        return [product for product in self.products if product.reviews <= 100]

    def top_3_bsr(self):
        """Returns the top 3 selling products
           Param: None
           Return type: list (ProductPage)"""
        top_bsr = sorted(self.products, key=lambda x: x.BSR)
        return top_bsr

    def bsr_over_25k(self):
        """Returns all the products that have over 25k BSR
           Param: None
           Return type: list (ProductPage)"""
        return [product for product in self.products if product.BSR > 25000]

    def avg_price(self):
        """Returns the average price of all the products found
           Param: None
           Return type: float"""
        price = 0.0
        for product in self.products:
            price += product.price
        return round(price / len(self.products), 2)

    def avg_bsr(self):
        """Returns the average BSRs of all the products
        Param: None
        Return type: int"""
        bsrs = 0
        excluded = 0
        for product in self.products:
            if product.BSR != 9999999999:
                bsrs += product.BSR
            else:
                excluded += 1
        return int(bsrs / len(self.products) - excluded)


class ProductPage:
    def __init__(self, url):
        self.valid = True
        self.has_been_validated = False
        self.url = url
        self.title = ""
        self.reviews = 0
        self.BSR = -1
        self.seller = {"name": "", "url": ""}
        self.rating = 0.0
        self.price = 0.0
        self.errors = []
        self.parse_page()
        self.validate()

    def find_ugly_bsr(self, bs):
        """Brute force method for finding BSR
           Param: bs (beautifulSoup object)
           Return type: int"""
        try:
            table = bs.find('table', id='productDetails_detailBullets_sections1')
            for tr_tag in table.find_all('tr'):
                if 'best seller' in tr_tag.th.text.lower():
                    bsr_text = tr_tag.td.text
                    bsr = re.search('(\d+(,\d+)?)', bsr_text).group().replace(',', '')
                    return int(bsr)
        except AttributeError:
            try:
                sales_rank_table = bs.find('tr', id='SalesRank')
                bsr_text = sales_rank_table.find('td', {'class': 'value'}).text
                bsr = re.search('(\d+(,\d+)?)', bsr_text).group(0).replace(',', '')
                return int(bsr)
            except AttributeError:
                return -1

    def parse_page(self):
        """Accepts a url string for an Amazon product page and parses it using BS
           Param: url (string)
           Return type: void"""
        # Create the Bs object
        bs = legit_bs(self.url)
        if bs.title.text.strip() == 'Amazon.com Page Not Found':
            # If the page is not found, set page's validity to false (so it won't be added to AmzPage and return void to stop parsing it)
            self.valid = False
            return

        # Set product's title
        try:
            self.title = bs.find("h1", {'id': "title"}).text.strip() or bs.find("div", id="title_feature_div").text.stirp()
        except AttributeError:
            self.errors.append("Couldn't fetch title")

        # Set product's seller name & url

        try:
            seller_info = bs.find("div", id="bylineInfo_feature_div")
            if not seller_info:
                seller_info = bs.find("span", id="merchantInfo").a
                self.seller['url'] = AMZ_URL + seller_info["href"]
            else:
                self.seller['url'] = AMZ_URL + seller_info.a["href"]
            self.seller['name'] = seller_info.text.strip()
        except AttributeError:
            self.seller['name'] = "Amazon"
            self.seller['url'] = AMZ_URL
        except TypeError:
            self.seller['name'] = "Unknown"
            self.seller['url'] = AMZ_URL

        # Set product's rating and reviews

        customer_info = bs.find("div", {"id": "averageCustomerReviews"})
        try:
            reviews_str = re.search('(\d+(,\d+)?)', customer_info.find("span", id="acrCustomerReviewText").text).group().replace(',', '')
            self.reviews = int(reviews_str)
        except AttributeError:
            self.errors.append('Could not find reviews')
        try:
            ratings_str = customer_info.find("span", {"class": "a-icon-alt"}).text
            self.rating = float(ratings_str[:3])
        except AttributeError:
            self.errors.append('Could not find ratings')

        # Set product's BSR

        try:
            bsr_str = bs.find('li', id="SalesRank") or bs.find('li', {"class": "zg_hrsr_item"})
            bsr = re.search('(\d+(,\d+)?)', bsr_str.text)
            if bsr.group() == '0':
                bsr_str = bs.find('span', {'class': "zg_hrsr_rank"}).text
                bsr = re.search('(\d+(,\d+)?)', bsr_str)
            bsr = bsr.group().replace(',', '')
            self.BSR = int(bsr)
        except AttributeError:
            self.BSR = self.find_ugly_bsr(bs)

        if self.BSR in ['', ' ', 0, -1, None]:
            self.BSR = 9999999999
            self.errors.append('Could not find BSR')

        # Set product's price

        try:
            price_str = bs.find("span", id="priceblock_ourprice") or bs.find('tr', id="priceblock_saleprice_row") or bs.find("div", id="price") or bs.find("div", id="buyNewSection")
            price = re.findall('\d+\.?\d{0,2}', price_str.text)[0]
            self.price = float(price)
        except IndexError:
            # Price not found
            pass
        except AttributeError:
            pass

        if self.price == 0.0:
            try:
                price = 0.0
                price_bs = bs.find_all("span", id=re.compile("style_name_\d_price"))
                for price_tag in price_bs:
                    price_str = re.findall('\d+\.?\d{0,2}', price_tag.text)[0]
                    price += float(price_str)
                self.price = round(price / len(price_bs), 2)
            except ZeroDivisionError:
                self.price = self.price_from_offers(self.url)

        if self.price == 0.0:
            self.errors.append("Could not find price")

    def price_from_offers(self, url):
        """Finds for given product when price is unavailable on the main product page, and therefore needs to be scraped from the offers page
           Param: url (string)
           Return type float"""
        asin = re.sub('http.*/', '', url)
        bs = legit_bs('https://www.amazon.com/gp/offer-listing/{0}/ref=dp_olp_new_mbc?ie=UTF8&condition=new'.format(asin))
        if not bs:
            # Because legit_bs returns false if it can't parse the page (broken link - 404 for example), then price can't be scraped.
            return 0.0

        try:
            price_str = bs.find('span', {'class': 'a-size-large a-color-price olpOfferPrice a-text-bold'}).text.strip()
            return float(price_str.replace('$', '').replace(',', ''))
        except AttributeError:
            return 0.0

    def to_csv(self):
        return {'url': self.url.encode('utf-8'), 'title': self.title.encode('utf-8'),
                'reviews': self.reviews, 'bsr': self.BSR, 'seller_name': self.seller['name'].encode('utf-8'),
                'seller_url': self.seller['url'].encode('utf-8'), 'rating': self.rating, 'price': self.price}

    def __repr__(self):
        """Like a Java's toString() method
           Input: None
           Return type: string"""
        return "%s (%s)" % (self.title.encode('utf-8'), self.BSR)

    def validate(self):
        """Validates the page was fully scraped with the correct information by checking the amount of errors appended to self.errors array
        Param: None
        Return type: None"""
        if len(self.errors) > 2:
            self.errors = []
            self.parse_page()


def main(keywords):
    """Main function for thread work - creates an AmzPage instance for given keywords, and when done attempts to create an CSV file parsing the data
       Param: keywords (string)
       Return type: None"""
    page = AmzPage(keywords)
    print "Found %d products on page (not including sponsored items) for %s" % (len(page.products), keywords)
    try:
        create_csv(keywords, page)
    except IOError:
         print 'Failed to create excel file for %s' % keywords


def force_make_file_path(keywords, count=0):
    """Generates new files if they already exist
       Param: keywords (string), count (recursive int)"""
    kws = keywords if count == 0 else keywords + '_{0}'.format(count)
    root_path = path + '\\' + kws + '.csv'
    if not os.path.isfile(root_path):
        return root_path
    return force_make_file_path(keywords, count=count+1)


def create_csv(keywords, page):
    """Creates an CSV file titled (keywords) with data from AmzPage page
       Param: keywords (string), page (AmzPage) retry=False (boolean)
       Return type: None"""

    csv_file_path = force_make_file_path(keywords)
    with open(csv_file_path, 'wb') as csvfile:
        fields = ['url', 'keywords', 'top_words']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fields)
        csv_writer.writeheader()
        csv_writer.writerow({})
        csv_writer.writerow(page.to_csv())
        csv_writer.writerow({})
        fields = ['url', 'title', 'reviews', 'bsr', 'seller_name', 'seller_url', 'rating', 'price']
        csv_writer.writerow({})
        csv_writer = csv.DictWriter(csvfile, fieldnames=fields)
        csv_writer.writeheader()
        csv_writer.writerow({})
        for _product in page.products:
            csv_writer.writerow(_product.to_csv())
        csv_writer.writerow({})
        fields = ['top_3_bsr', 'avg_price', 'over_800_revs', 'under_100_revs', 'bsr_over_25k', 'avg_bsr']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fields)
        csv_writer.writerow({})
        csv_writer.writeheader()
        csv_writer.writerow({})
        data = {'avg_price': page.avg_price(), 'over_800_revs': len(page.over_800_revs()),
                'under_100_revs': len(page.under_100_revs()), 'bsr_over_25k': len(page.bsr_over_25k()), 'avg_bsr': page.avg_bsr()}
        csv_writer.writerow(data)
        csv_writer.writerows([{'top_3_bsr': bsr} for bsr in page.top_3_bsr()[0:3]])
        if page.errors:
            csv_writer.writerow({})
            fields = ['errors']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fields)
            csv_writer.writeheader()
            csv_writer.writerow({})
            csv_writer.writerows([{'errors': error} for error in page.errors])

    print 'Finished writing to %s' % csv_file_path


if __name__ == "__main__":
    print 'Hi Erez... any bugs tell Gal\nTo quit enter x'
    print 'Excel file output: %s' % path
    words = raw_input("Enter key words... ")
    while words.lower() != 'x':
        try:
            next_thread = threading.Thread(target=main, args=(words,), name=words)
            thread_pool.append(next_thread)
            thread_pool[-1].start()
            print 'Search started: %s' % words
            words = raw_input("Enter key words... ")
            if words == '':
                words = raw_input('Invalid input, please try again..')
            elif words.lower() == 'x':
                print 'Waiting for all threads to terminate before closing... please do not attempt to close before all threads are finished'
                for thread in thread_pool:
                    thread.join()
                print 'Bye!'
                time.sleep(2)

        except Exception, e:
            print 'Unknown error occured: %s\nPlease tell Gal..' % e.message
            time.sleep(2)
            sys.exit(1)


