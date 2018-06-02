import xlrd
import csv
import urllib
import os
import random
import threading
import os.path
import xlsxwriter
import datetime
import TracerUtils
from tkinter import *
from tkFileDialog import askopenfilename, askdirectory
from time import sleep


AMAZON_SEARCH_URL = "https://www.amazon.com/s/keywords="
AMZ_SEARCH_BY_PAGE_URL = 'https://www.amazon.com/s/page={0}&keywords={1}&ie=UTF8'
DEFAULT_ASIN = "B078YBWH54"
lock = threading.Lock()


class Application:

    def __init__(self):
        self.root = Tk()
        self.root.title("IndexFinder v0.01")
        self.root.geometry("500x200")
        self.button_frame = Frame(self.root, height=30, width=50)

        self.choose_file_btn = Button(self.button_frame, text="Choose File...")
        self.choose_file_btn.bind("<Button-1>", self.get_xls_file_path)
        self.start_btn = Button(self.button_frame, text="Start")
        self.start_btn.bind("<Button-1>", self.start_find_indexation)
        self.generate_csv_btn = Button(self.button_frame, text="Generate xlsx")
        self.generate_csv_btn.bind("<Button-1>", self.generate_csv)

        self.file_name_entry = Entry(self.root, justify='center')
        self.file_name_entry = Entry(self.root, width=60)
        self.file_name_entry.bind("<Button-1>", self.get_xls_file_path)

        self.button_frame.pack(side=BOTTOM)
        self.file_name_entry.pack(side=BOTTOM)
        self.choose_file_btn.pack(side=LEFT)
        self.start_btn.pack(side=RIGHT)

        self.results = []
        self.status_label = Label(self.root, text="Waiting")
        self.asin_entry = Entry(self.root, justify='center')
        self.asin_entry.insert(END, "B078YBWH54")
        self.status_label.pack()
        self.asin_entry.pack(side=BOTTOM)

        self.results_listener = threading.Thread(target=self.listen_to_results)

    def get_xls_file_path(self, event):
        file_path = askopenfilename(initialdir=os.environ['USERPROFILE'])
        self.file_name_entry.delete(0, END)
        self.file_name_entry.insert(0, file_path)

    def start_find_indexation(self, event):
        print 'starting',
        if threading.active_count() < 2 and self.file_name_entry.get():
            threading.Thread(target=find_indexation_for_terms, args=(self.results, self.status_label, None, DEFAULT_ASIN, self.file_name_entry.get())).start()
            self.results_listener.start()
        else:
            top_level = Toplevel(self.root)
            label_warning = Label(top_level, text="A search is already in progress!")
            label_warning.pack()

    def start(self):

        self.root.mainloop()

    def listen_to_results(self):
        while True:
            if self.results:
                with lock:
                    self.generate_csv_btn.pack(side=RIGHT)
                    print 'Generate CSV button enabled'
                    break

    def generate_csv(self, event):
        asin = self.asin_entry.get()
        work_dir = askdirectory(initialdir=os.environ['USERPROFILE'])
        path = os.path.join(work_dir, 'indexFinder', asin)
        threading.Thread(target=create_csv, args=(self.results, path)).start()


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
        return AMAZON_SEARCH_URL + urllib.quote((search_term + "+" + asin).encode('utf-8'))

    return AMZ_SEARCH_BY_PAGE_URL.format(page, urllib.quote(search_term.encode('utf-8')))


def get_page_bs_element(search_term, asin=DEFAULT_ASIN, page=-1):

    url = build_url(search_term, asin, page)
    return TracerUtils.legit_bs(url)


def get_all_products(bs_object):

    pattern = re.compile('result_\d+')
    try:
        return [product for product in bs_object.find_all('li', {'id': pattern}) if not product.find('h5')]
    except AttributeError:
        return []


def product_found_in_page(products, asin=DEFAULT_ASIN):

    for product in products:
        if product.has_attr('data-asin'):
            if product['data-asin'] == asin:
                print product['id']
                return int(re.search('\d+', product['id']).group(0))
    return 0


def get_page_of_product(search_term, label_to_update=None, asin=DEFAULT_ASIN):

    for i in xrange(20, 0, -1):
        sleep(random.uniform(0, 1))
        print 'page', i, '/', search_term
        if label_to_update:
            label_to_update['text'] = 'page ' + str(i) + ' / ' + search_term
        bs = get_page_bs_element(search_term, asin, i)
        products = get_all_products(bs)
        index = product_found_in_page(products, asin)
        if index:
            print asin, 'found in page', i, 'index ', index
            if label_to_update:
                label_to_update['text'] = asin + ' found in page ' + str(i) + ' index ' + str(index) + '(%s)' % search_term
            with lock:
                return {'term': search_term, 'page': i, 'index': index}
    with lock:
        return {'term': search_term, 'page': -1, 'index': -1}


def product_is_indexed(search_term, asin=DEFAULT_ASIN):
    bs = get_page_bs_element(search_term, asin)
    if not bs.find('h1', id="noResultsTitle"):
        print asin, 'indexed for', search_term
        return True
    return False


def get_search_terms_from_file(file_path):
    extension = os.path.splitext(file_path)[1]
    if extension in ['.xls', '.xlsx']:
        return get_search_terms_from_xlsx(file_path)
    elif extension == '.csv':
        return get_search_terms_from_csv(file_path)
    raise ValueError("Bad file provided")


def get_search_terms_from_csv(csv_path):
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        search_terms = []
        for row in reader:
            search_terms.append(row[0])
        return search_terms


def get_search_terms_from_xlsx(xlsx_path):
    reader = xlrd.open_workbook(xlsx_path).sheet_by_index(0)
    search_terms = []
    for row in range(reader.nrows):
        if not reader.cell(row, 0).ctype == xlrd.XL_CELL_EMPTY:
            search_terms.append(reader.cell(row, 0).value)
    return search_terms


def find_indexation_for_terms(results, label_to_update=None, search_terms=None, asin=DEFAULT_ASIN, from_file=None):

    if from_file:
        search_terms = get_search_terms_from_file(from_file)

    def _find_indexation_for_terms(_results, _search_terms, _asin=DEFAULT_ASIN):

        for search_term in _search_terms:
            if type(search_term) is list:
                search_term = search_term[0]
            print 'Search term -', search_term
            with lock:
                if label_to_update:
                    label_to_update['text'] = 'Search term - ' + search_term
            if product_is_indexed(search_term, _asin):
                _results.append(get_page_of_product(search_term, label_to_update, _asin))

    terms_divided = split_five(search_terms)

    for terms in terms_divided:
        threading.Thread(target=_find_indexation_for_terms, args=(results, terms, asin)).start()


def create_csv(results, path):
    print 'create_csv called'
    now = datetime.datetime.now().strftime('%m.%d.%Y %H.%M')
    if not os.path.exists(path):
        os.makedirs(path)
    excel = xlsxwriter.Workbook(path + '\\' + now + '.xlsx')
    excel.add_worksheet("Results")

    sheet = excel.get_worksheet_by_name("Results")

    sheet.write(0, 0, "Search Term")
    sheet.write(0, 1, "Index")
    sheet.write(0, 2, "Page")
    sheet.write(0, 3, "RealPage")

    r = 1

    print results

    for result in results:
        sheet.write(r, 0, result['term'])
        sheet.write(r, 1, result['index'])
        sheet.write(r, 2, result['page'])
        sheet.write(r, 3, int(result['page']/16))
        r += 1

    excel.close()


def split_five(arr):
    length = len(arr)
    result = []
    interval = int(length/5)
    for i in range(5):
        result.append(arr[i*interval:(i+1)*interval])

    result[-1].append(arr[5*interval:])

    return result


if __name__ == "__main__":

    # dic = find_indexation_for_terms(["construction magnets"], DEFAULT_ASIN)
    # print dic

    app = Application()

    app.start()
