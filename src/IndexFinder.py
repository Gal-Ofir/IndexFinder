import requests
from bs4 import BeautifulSoup as Bs
import xlrd
import csv
import urllib
import os
import random
import codecs
import threading
import os.path
from tkinter import *
from tkFileDialog import askopenfilename

global file_name_entry, root
generate_csv_btn = None
AMAZON_SEARCH_URL = "https://www.amazon.com/s/keywords="
AMZ_SEARCH_BY_PAGE_URL = 'https://www.amazon.com/s/page={0}&keywords={1}&ie=UTF8'
DEFAULT_ASIN = "B078YBWH54"


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


def build_url(search_term, asin=DEFAULT_ASIN, page=-1):

    if page == -1:
        return AMAZON_SEARCH_URL + urllib.quote(search_term + "+" + asin)

    return AMZ_SEARCH_BY_PAGE_URL.format(page, urllib.quote(search_term))


def get_page_bs_element(search_term, asin=DEFAULT_ASIN, page=-1):

    url = build_url(search_term, asin, page)
    return Bs(requests.get(url, headers=rnd_user_agent()).text, 'html.parser')


def get_all_products(bs_object):

    pattern = re.compile('result_\d+')
    return [product for product in bs_object.find_all('li', {'id': pattern}) if not product.find('h5')]


def product_found_in_page(products, asin=DEFAULT_ASIN):

    for product in products:
        if product.has_attr('data-asin'):
            if product['data-asin'] == asin:
                return True
    return False


def get_page_of_product(search_term, asin=DEFAULT_ASIN):

    for i in xrange(1, 21):
        print 'page', i, '/', search_term
        bs = get_page_bs_element(search_term, asin, i)
        products = get_all_products(bs)
        if product_found_in_page(products, asin):
            print asin, 'found in page', i
            return i

    return -1


def product_is_indexed(search_term, asin=DEFAULT_ASIN):
    if not get_page_bs_element(search_term, asin).find('h1', id="noResultsTitle"):
        print asin, 'indexed for', search_term
        return True
    return False


def get_search_terms_from_file(filepath):
    extension = os.path.splitext(filepath)[1]
    if extension in ['.xls', '.xlsx']:
        return get_search_terms_from_xlsx(filepath)
    elif extension == '.csv':
        return get_search_terms_from_csv(filepath)
    raise ValueError("Bad file provided")


def get_search_terms_from_csv(csvpath):
    with open(csvpath, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        search_terms = []
        for row in reader:
            search_terms.append(row[0])
        return search_terms


def get_search_terms_from_xlsx(xlsxpath):
    reader = xlrd.open_workbook(xlsxpath).sheet_by_index(0)
    search_terms = []
    for row in range(reader.nrows):
        search_terms.append(reader.cell(row, 0).value)
    return search_terms


def find_indexation_for_terms(search_terms=None, asin=DEFAULT_ASIN, from_file=None):
    if from_file:
        search_terms = get_search_terms_from_file(from_file)
    index_results = {}
    for search_term in search_terms:
        print 'Search term -', search_term
        if product_is_indexed(search_term, asin):
            index_results[search_term] = get_page_of_product(search_term, asin)
    return index_results


def hievent(event):
    filepath = askopenfilename()
    file_name_entry.delete(0)
    file_name_entry.insert(0, filepath)


def byeevent(event):
    print 'starting'
    results = find_indexation_for_terms(None, DEFAULT_ASIN, file_name_entry.get())
    enable_generate_csv(results)


def enable_generate_csv(results):
    global generate_csv_button
    generate_csv_button = Button(root, "Generate xls file", command=lambda: create_csv(results))
    generate_csv_button.pack()


def create_csv(results):
    # TODO THIS
    pass


if __name__ == "__main__":

    # dic = find_indexation_for_terms(["construction magnets"], DEFAULT_ASIN)
    # print dic

    root = Tk()
    root.title("IndexFinder v0.01")
    root.geometry("500x200")
    button_frame = Frame(root, height=30, width=50)
    choose_file_btn = Button(button_frame, text="Choose File...")
    choose_file_btn.bind("<Button-1>", hievent)
    start_btn = Button(button_frame, text="Start")
    start_btn.bind("<Button-1>", byeevent)
    file_name_entry = Entry(root, width=80)
    button_frame.pack(side=BOTTOM)
    file_name_entry.pack(side=BOTTOM)
    choose_file_btn.pack(side=LEFT)
    start_btn.pack(side=RIGHT)

    root.mainloop()
