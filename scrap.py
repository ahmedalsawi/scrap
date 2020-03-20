
import requests 
from bs4 import BeautifulSoup
import re
import argparse
import logging

import requests_cache

requests_cache.install_cache('demo_cache')

URL = "https://forums/"

def get_threads(search_text):
  results = []

  for pagenum in range(1,15):
    new_page = "{}search.asp?q={}&f=762&t=0&p={}".format(URL , search_text, pagenum)
    r = requests.get(new_page)
    
    logging.info("Requesting Page {}".format(new_page))

    soup = BeautifulSoup(r.content, 'html5lib') 
    threads = soup.find('li', attrs = {'class':'search1'}).findAll('a', attrs = {'title':'View This Message'})

    for thread in threads:
      result = {}
      result['heading']= thread.text
      result['href']= URL + thread['href'].replace('fm','am')
      results.append(result)
  return(results)

def search_thread(thread,search_text):
    logging.info("Searching Page {}".format(thread['href']))
    r = requests.get(thread['href'])
    soup = BeautifulSoup(r.content, 'html5lib')


    posts = [p.findAll('div')[0].text for p in soup.findAll('div', attrs = {'class':'am_body_left'})]

    blob = '\n'.join(posts)
    # TODO clean up the posts
    blob = re.sub('\n+','\n',blob)
    blob = re.sub('Advertisemen.*','',blob)


    results = [re.search(txt,blob,re.IGNORECASE) for txt in search_text]
    logging.info(results)

    if None not in results:
      print("\n\n")
      print(thread)
      print("\n\n")

      
def sanitize(str1):
   res = '+'.join(re.findall(r'\w+', str1))
   return res

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='something something')
  parser.add_argument('-i', action="store_true", default=False, help="Ignore case")
  parser.add_argument('-verbose', action="store_true", default=False, help="Enable more loogin")

  parser.add_argument('text')
  
  args = parser.parse_args()

  
  logging.basicConfig(level=logging.INFO)


  threads= get_threads(sanitize(args.text))

  logging.info("Found {}".format(len(threads)))
  req_text = []
  req_text += (re.sub('"([^"]*)"','',args.text).strip().split())
  req_text += (re.findall('"([^"]*)"', args.text))
  assert(len(req_text) !=0 )

  for thread in threads:
    search_thread(thread, req_text)
