import requests
import threading
import argparse
import queue
from requests_pkcs12 import Pkcs12Adapter
import urllib3
import time
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='P12 Url Fuzzer with Curl, by my-0day')

parser.add_argument('-w','--wordlist', dest='wordlist_path', type=str, help='Wordlist Path')
parser.add_argument("-u","--url", dest="url", type=str, help="Url to Fuzz", required=True)
#parser.add_argument("--cert-type", dest="cert_type", type=str, help="Certificate Type (P12, PEM, CRT...)")
parser.add_argument("--p12",dest="cert_path", help="P12 Path, Format (Path/Cert.p12:password)")
parser.add_argument("-k","--verify",dest="verify",type=str,help="SSL Verify? (True/False|1/0)")
parser.add_argument("-t","--threads",type=int, dest="threads",help="Number of threads")
parser.add_argument("-x","--extension",type=str,dest="extension",help="File Ext (php,txt,html,bak...)")
args = parser.parse_args()
if args.threads == None:
    threads=15
else:
    threads=args.threads

s=requests.Session()
if args.cert_path is not None:
    if ":" not in args.cert_path:
        print("WRONG P12 FORMAT")
        raise SystemExit
    p12_path,p12_pass=args.cert_path.split(":")
    s.mount(args.url, Pkcs12Adapter(pkcs12_filename=p12_path, pkcs12_password=p12_pass))

url = args.url
if "FUZZ" not in url:
    if url[-1]!="/":
        url=url+"/"

if args.wordlist_path == None:
    wordlist_path="/usr/share/wordlists/dirb/common.txt"
else:
    wordlist_path=args.wordlist_path

if args.verify != None:
    if "rue" in args.verify or "1" in args.verify:
        s.verify=True
    else:
        s.verify=False
else:
    s.verify=True

word_queue=queue.Queue()
if args.extension is not None:
    ext=args.extension
    if ext[0] != ".":
        ext="."+ext
if args.extension is not None:
    for els in open(wordlist_path,"r").read().splitlines():
        word_queue.put(els)
        word_queue.put(els+ext.strip())
else:
    for els in open(wordlist_path,"r").read().splitlines():
        word_queue.put(els)

f_responses=[]

def worker(url):
    global word_queue
    global s
    global cert_type
    global cert_path
    global f_responses
    if word_queue.empty():
        return
    while 1:
        if word_queue.empty():
            return
        path=word_queue.get()
        if "FUZZ" not in url:
            final_url = url+path
        else:
            final_url=url.replace("FUZZ",path)
        r=os.popen(f"curl -s -k -X GET -w  "+'%{stdout}%{response_code}'+f" --cert-type P12 --cert {p12_path}:{p12_pass} \"{final_url}\"")
        res = r.read()
        if len(res) > 4:
            status = res[-3:]
        if res not in f_responses and "404" not in status:
            f_responses.append(res)
            print(f"[ {status} ] {path} - {final_url}")
        time.sleep(0.05)

threads_list=[]
for t in range(threads):
    threads_list.append(threading.Thread(target=worker,args=(url,)))
for t in threads_list:
    t.start()
for t in threads_list:
    t.join()



