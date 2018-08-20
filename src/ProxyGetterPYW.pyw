import threading
import os
from TracerUtils import get_proxies

proxy_sites = ['https://www.us-proxy.org/', 'https://www.sslproxies.org/', 'https://free-proxy-list.net/',
               'https://free-proxy-list.net/anonymous-proxy.html', 'https://free-proxy-list.net/uk-proxy.html']

lock = threading.Lock()

app_data_path = os.environ["APPDATA"] + '\\Proxy Getter\\'

if __name__ == '__main__':
    with lock:
        with(open(app_data_path + 'proxy_list.txt', 'a')) as proxy_list:

            for proxy in get_proxies():

                proxy_list.write(str(proxy))
                proxy_list.write('\n')
