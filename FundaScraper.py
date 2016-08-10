# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 11:41:00 2016

@author: luuk
"""

# coding=utf-8
import csv
from datetime import date
import httplib
import re
import sys
import logging
import urllib2
from urllib2 import URLError
import urlparse
from datetime import datetime
import time

import mechanize
import requests
from bs4 import BeautifulSoup


MAIN_URL = 'http://www.funda.nl/koop/amsterdam'
VERKOCHT_URL = 'http://www.funda.nl/koop/verkocht/amsterdam'

DATA_DIR = "C:\Users\Luuk\Stock prices\Stadsdeel\data"

# To make sure you're seeing all debug output:
logger = logging.getLogger("mechanize")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

# normalize house types
# change link to oversight

def scrape_links(br):
    print str(datetime.now()) + " " + br.geturl(),'test'
    links = list()
    for link in br.links(url_regex='/koop/'):
        IMG = '[IMG]'
        if IMG in link.text:
            links.append(urlparse.urljoin(link.base_url, link.url + "kenmerken"))

    return links


def get_html(link):
    while True:
    # try:
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7'}
        # request = urllib2.Request(link, headers=headers)
        # response = urllib2.urlopen(request)

        response = requests.get(link.rstrip())

        if "fout/500" in response.url:
            print str(datetime.now()) + " ... retrying " + response.url
            continue
        break
        # except URLError as e:
        #     print str(datetime.now()) + " [Errno 54] Connection reset by peer .. sleeping"
        #     time.sleep(2)
        # except IOError as e:
        #     print str(datetime.now()) + " IOError .. sleeping"
        #     time.sleep(2)

    if "fout/404" not in response.url and "fout/500" not in response.url:
        html = response.text
        if "Object niet (meer) beschikbaar" not in html:
            return html
    else:
        print str(datetime.now()) + " ... failed " + response.url
    return None



def parse_html(html):
    #try:
    soup = BeautifulSoup(html)
    specs = {}
    specs["Address"] = soup.find("h1", class_="object-header-title").text
    specs["Postcode"] = soup.find("span", class_="object-header-subtitle").text

    for table in soup.find_all("dl", class_="object-kenmerken-list"):
        for dt,dd in zip(table.find_all('dt'),table.find_all('dd')):
            if 'gebruiksoppervlakten' in dt:
                'continue'
                continue
            print dt,dd,'dt,dd'
            if dt.get_text(strip=True):
                key = dt.get_text(strip=True)
                text = dd.get_text("|", strip=True)
                text = text.replace(u"\u00B2", u'')  # replace squares
                text = text.replace(u"\u00B3", u'')  # replace cubes
                text = re.sub("\W+m$", "", text)  # replace metres
                text = text.replace(u"\u20AC", u'').strip()  # replace euros
                text = text.replace(u"\xb2", u'').strip()
                print key,text
                if 'gebruiksoppervlakten' in key.lower():
                    'continue'                    
                    continue
                if 'gebruiksoppervlakten' in text.lower():
                    'continue'                    
                    continue
                if 'kadastrale' in key.lower():
                    'continue'                    
                    continue
                if 'kadastrale' in text.lower():
                    'continue'                    
                    continue
                #    key = 'kadastrale kaart'
                #    print key
                if key in ['Vraagprijs', 'Laatste vraagprijs', 'Oorspronkelijke vraagprijs']:
                    if "v.o.n." in text:
                        text = text.replace(" v.o.n.", "")
                        specs["Cost"] = "v.o.n."
                    elif "k.k." in text:
                        text = text.replace(" k.k.", "")
                        specs["Cost"] = "k.k."
                    text = text.replace(".", "")
                
                
                specs[key] = text
    return specs
    #except BaseException as e:
    #    print str(datetime.now()) + " ... failed: " + e.message, 1
    #    return None


def get_all_keys(all_specs):
    keys = set()
    for specs in all_specs:
        keys.update(specs.keys())
    return sorted(list(keys))


def write_test_file(link, html):
    with open("data/" + link.split('/')[-2] + ".html", "w") as text_file:
        text_file.write(html.read())
        # parse_html(html)


def write_links(datestr):
    br = mechanize.Browser()
    time.sleep(1)
    while True:
        try:
            br.open(MAIN_URL)
            break
        except URLError as e:
            print str(datetime.now()) + " [Errno 54] Connection reset by peer .. sleeping"
            time.sleep(1)
    links = list()
    volgende = True
    count = 0
    while volgende is True:
        try:
            links.extend(scrape_links(br))
            br.follow_link(text_regex="^Volgende", nr=0)
            count += 1
            print count
            print scrape_links(br),'scrape'
            if count > 60: # This count maximises iterations 
                print 'break'                
                break
        except URLError as e:
            print str(datetime.now()) + " [Errno 54] Connection reset by peer .. sleeping"
            time.sleep(1)
        except httplib.BadStatusLine as e:
            print str(datetime.now()) + " BadStatusLine .. sleeping"
            time.sleep(1)
        except mechanize.LinkNotFoundError:
            volgende = False

    with open(DATA_DIR + datestr + "-links.txt", 'wb') as fou:
        fou.write("\n".join(links))


def read_links(datestr):
    with open(DATA_DIR + datestr + "-links.txt", 'r') as f:
        return f.readlines()


def process_koop():
    datestr = date.today().isoformat()
    write_links(datestr)
    links = read_links(datestr)
    all_specs = list()
    for link in links:
        try:
            print str(datetime.now()) + " " + link +' verif'
            try:
                html = get_html(link)
            except:
                html = None
            if html is not None:
                specs = parse_html(html)
                
                specs["Id"] = parse_id(link)
                specs["Link"] = '=HYPERLINK("' + link.replace('kenmerken', '') + '")'
                all_specs.append(specs)
        except:
            continue
    keys = get_all_keys(all_specs)
    suffix = MAIN_URL.split('/')[-1]
    with open(DATA_DIR + datestr + '-' + suffix + ".csv", 'wb') as fou:
        fou.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
        dw = csv.DictWriter(fou, fieldnames=keys)
        try:
            dw.writeheader()
        except:
            None
        for specs in all_specs:
            dw.writerow({k: v.encode('utf8') for k, v in specs.items()})


def parse_id(link):
    regex = re.compile("-(\d+)-")
    r = regex.search(link)
    return r.groups()[0]


def process_verkocht():
    br = mechanize.Browser()
    while True:
        try:
            br.open(VERKOCHT_URL)
            break
        except URLError as e:
            print str(datetime.now()) + " [Errno 54] Connection reset by peer .. sleeping"
            time.sleep(1)

    links = list()
    volgende = True
    count = 0
    while volgende is True:
        try:
            links.extend(scrape_links(br))
            br.follow_link(text_regex="^Volgende", nr=0)
            count += 1
            if count > 0: # This count maximises iterations, must be adjusted if you want to scrape more than one page 
                break
        except httplib.BadStatusLine as e:
            print str(datetime.now()) + " BadStatusLine .. sleeping"
            time.sleep(1)
        except URLError as e:
            print str(datetime.now()) + " [Errno 54] Connection reset by peer .. sleeping"
            time.sleep(1)
        except mechanize.LinkNotFoundError:
            volgende = False

    datestr = date.today().isoformat()
    with open(DATA_DIR + datestr + "-verkocht-links.txt", 'wb') as fou:
        fou.write("\n".join(links))
    all_specs = list()
    print links
    for link in links:

        print str(datetime.now()) + " " + link
        try:
            html = get_html(link)
        except:
            continue
        try:
                
            if html is not None:
                specs = parse_html(html)
                specs["Id"] = parse_id(link)
                specs["Link"] = '=HYPERLINK("' + link.replace('kenmerken', '') + '")'
                all_specs.append(specs)
        except:
            continue

    keys = get_all_keys(all_specs)
    suffix = MAIN_URL.split('/')[-1]
    with open(DATA_DIR + datestr + '-verkocht-' + suffix + ".csv", 'wb') as fou:
        fou.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
        dw = csv.DictWriter(fou, fieldnames=keys)
        dw.writeheader()
        for specs in all_specs:
            dw.writerow({k: v.encode('utf8') for k, v in specs.items()})


def main(): # determine which function to execute 
    process_koop()
    #process_verkocht()
    return None

if __name__ == "__main__":
    main()




