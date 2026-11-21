#!/usr/bin/env python3
"""Google Play search results and listing text for seed queries (public pages, US English).
usage: play_listings.py "seed one" "seed two" ...   -> play-search.csv, play-listings.csv, play-listings.json"""
import sys,re,json,csv,html,urllib.request,urllib.parse,time
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36','Accept-Language':'en-US,en;q=0.9'}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read().decode('utf8','replace')
def search(q):
    h=get('https://play.google.com/store/search?'+urllib.parse.urlencode({'q':q,'c':'apps','hl':'en_US','gl':'US'}))
    ids=[]
    for i in re.findall(r'/store/apps/details\?id=([A-Za-z0-9_.]+)',h):
        if i not in ids: ids.append(i)
    return ids
def listing(i):
    h=get('https://play.google.com/store/apps/details?'+urllib.parse.urlencode({'id':i,'hl':'en_US','gl':'US'}))
    def m(p,f=0):
        x=re.search(p,h,re.S|f); return html.unescape(re.sub(r'<[^>]+>',' ',x.group(1))).strip() if x else ''
    title=m(r'<h1[^>]*>(.*?)</h1>')
    short=m(r'<meta itemprop="description" content="(.*?)">')
    full=m(r'data-g-id="description"[^>]*>(.*?)</div>')
    inst=m(r'>([0-9.,]+[KMB]?\+)</div><div[^>]*>Downloads')
    rating=m(r'aria-label="Rated ([0-9.]+) stars')
    dev=m(r'<a href="/store/apps/dev[^"]*"[^>]*><span>(.*?)</span>')
    return dict(id=i,title=title,short=short,installs=inst,rating=rating,developer=dev,full=full)
if __name__=='__main__':
    rows=[];order=[]
    for q in sys.argv[1:]:
        try: ids=search(q)
        except Exception as e: print(q,'ERR',e); continue
        print(q,len(ids),ids[:5])
        for n,i in enumerate(ids[:12],1):
            rows.append(dict(query=q,rank=n,id=i))
            if i not in order: order.append(i)
        time.sleep(1)
    csv.DictWriter(open('play-search.csv','w',newline=''),fieldnames=['query','rank','id']).writeheader()
    w=csv.DictWriter(open('play-search.csv','a',newline=''),fieldnames=['query','rank','id']); w.writerows(rows)
    out=[]
    for i in order:
        try: out.append(listing(i))
        except Exception as e: out.append(dict(id=i,title='ERR '+str(e)))
        time.sleep(0.6)
    json.dump(out,open('play-listings.json','w'),indent=1)
    print(len(out),'listings')
