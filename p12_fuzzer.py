import requests
import threading
import argparse
import queue
from requests_pkcs12 import Pkcs12Adapter
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='P12 Url Fuzzer, by my-0day')

parser.add_argument('-w','--wordlist', dest='wordlist_path', type=str, help='Wordlist Path')
parser.add_argument("-u","--url", dest="url", type=str, help="Url to Fuzz", required=True)
#parser.add_argument("--cert-type", dest="cert_type", type=str, help="Certificate Type (P12, PEM, CRT...)")
parser.add_argument("--p12",dest="cert_path", help="P12 Path, Format (Path/Cert.p12:password)")
parser.add_argument("-k","--verify",dest="verify",type=str,help="SSL Verify? (True/False|1/0)")
parser.add_argument("-t","--threads",type=int, dest="threads",help="Number of threads")

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
if url[-1]=="/":
    url=url[:-1]

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
for els in open(wordlist_path,"r").read().splitlines():
    word_queue.put(els)



responses = queue.Queue()


def worker(url):
    global word_queue
    global s
    global cert_type
    global cert_path
    global responses
    if word_queue.empty():
        return
    while 1:
        if word_queue.empty():
            return
        path=word_queue.get()
        final_url = url+path
        r=s.get(final_url,verify=False)
        responses.put({r:path})
def handle_responses():
    f_responses=[]
    while 1:
        if word_queue.empty():
            if responses.empty():
                return
        if not responses.empty():
            el=responses.get()
            r,path=list(el.items())[0]
            if r.status_code != 200 and r.text not in f_responses:
                f_responses.append(r.text)
                print(f"[{str(r.status_code)}] - {path} - {r.text} [{str(r.status_code)}]")
        else:
            time.sleep(0.2)
t2=threading.Thread(target=handle_responses)
t2.start()
threads_list=[]
for t in range(threads):
    threads_list.append(threading.Thread(target=worker,args=(url,)))
for t in threads_list:
    t.start()
for t in threads_list:
    t.join()
t2.join()


