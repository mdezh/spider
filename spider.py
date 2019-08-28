#!/usr/bin/python3

import argparse
import requests
import sys
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse
from urllib3 import disable_warnings

MAX_DEEP = 5

checkedUrls = {}

def getLinkTypeAndContent(link):
    try:
        if useOnlyGet:
            r = requests.get(link, headers = headers, allow_redirects=True, verify=False)
        else:
            r = requests.head(link, headers = headers, allow_redirects=True, verify=False)
        if r.status_code >= 400:
            return ('wrong', '')
        if r.status_code >= 300:
            return getLinkTypeAndContent(r.headers['location'])
        if '/html' in r.headers['content-type']:
            if useOnlyGet:
                return ('html', r.text)
            else:
                return ('html', requests.get(link, headers = headers, allow_redirects=True, verify=False).text)
    except:
        return ('wrong', '')
    return ('file', '')

def isChecked(url):
    if checkedUrls.get(url) == None:
        return False
    return True

def updateParents(url, parent):
    checkedUrls[url]['parents'] = checkedUrls[url]['parents'].union({parent})


def isUrlLocale(url):
    o = urlparse(url)
    return (o.scheme == '' and o.netloc == '') or (o.scheme == parsedStartUrl.scheme and o.netloc == parsedStartUrl.netloc)

def prepareLink(link):
    pos = link.find('#')
    if pos >= 0:
        link = link[0:pos]
    if len(link) < 1:
        return startUrl
    if link[-1] == '/':
        link = link[0:-1]
    if len(link) < 1:
        return startUrl
    o = urlparse(link)
    if o.scheme != '' or o.netloc != '':
        return link
    if link[0] != '/':
        link = '/' + link
    return startUrl + link

def getLinksFrom(content):
    soup = BeautifulSoup(content, 'html.parser', parse_only=SoupStrainer(['a', 'img']))
    urls_a = {link['href'] for link in soup if link.get('href')}
    urls_img = {link['src'] for link in soup if link.get('src')}
    links = [prepareLink(url) for url in urls_a.union(urls_img) if isUrlLocale(url)]
    links = [link for link in links if link != '']
    return links

def checkUrl(url, deepLevel, parent='START'):
    if showProgress:
        print(parent + ' :  ' + url)
    if isChecked(url):
        updateParents(url, parent)
        return
    (linkType, content) = getLinkTypeAndContent(url)
    checkedUrls[url] = {'type': linkType, 'parents': {parent}}
    if deepLevel == maxDeep:
        return
    if linkType == 'wrong' or linkType == 'file':
        return
    links = getLinksFrom(content)
    for link in links:
        checkUrl(link, deepLevel+1, url)

def getShortUrl(url):
    o = urlparse(url)
    shortUrl = o.path + o.params
    if o.query != '':
        shortUrl += '?' + o.query
    if shortUrl == '':
        shortUrl = '/'
    return shortUrl

def printUrls(urls, withParents=False):
    for url in urls:
        shortUrl = getShortUrl(url)
        if withParents:
            print(shortUrl + '\t\t', [getShortUrl(url) for url in checkedUrls[url]['parents']])
        else:
            print(shortUrl)
    print('Number: ', len(urls), '\n')

def createArgsParser():
    parser = argparse.ArgumentParser(
        description="Check the site for broken inner links in tags <a href=...> and <img src=...>",
    )
    parser.add_argument('-q', '--quiet', action='store_true', help='don\'t show work progress')
    parser.add_argument('-p', '--parents', action='store_true', help='show list of pages, where the link was used')
    parser.add_argument('-g', '--getonly', action='store_true', help='always use a GET request method instead of HEAD')
    parser.add_argument('-m', '--maxdeep', metavar='N', default=MAX_DEEP, type=int, help='maximum recursion level, default is '+str(MAX_DEEP))
    parser.add_argument('url', help='URL for links checking')
    return parser

def checkMaxDeep():
    if maxDeep < 0:
        print('N in --maxdeep N  may not be lesser than 0')
        exit(1)

def checkStartUrl():
    global startUrl, parsedStartUrl
    if startUrl[-1] == '/':
        startUrl = startUrl[0:-1]
    parsedStartUrl = urlparse(startUrl)
    if parsedStartUrl.scheme == '' or parsedStartUrl.netloc == '':
        print('url must have a scheme and host (like http://domain.com)')
        exit(1)


if __name__ != '__main__': exit()

argsParser = createArgsParser()
namespace = argsParser.parse_args()

startUrl = namespace.url
maxDeep = namespace.maxdeep
useOnlyGet = namespace.getonly
showParents = namespace.parents
showProgress = not namespace.quiet

checkStartUrl()
checkMaxDeep()


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
}

disable_warnings()

checkUrl(startUrl, 0)

print()

failedUrls = {url for url in checkedUrls if checkedUrls[url]['type'] == 'wrong'}
successedUrls = {url for url in checkedUrls if checkedUrls[url]['type'] != 'wrong'}

if showParents:
    print('Working links (with parents):')
    printUrls(successedUrls, True)
    print('Broken links (with parents):')
    printUrls(failedUrls, True)
else:
    print('Working links:')
    printUrls(successedUrls)
    print('Broken links:')
    printUrls(failedUrls)
