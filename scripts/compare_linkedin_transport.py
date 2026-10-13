import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit
import requests
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path("current/scripts/jobspy").resolve()))
from fetch_linkedin_requests import USER_AGENTS, parse_search
from linkedin_http import block_page, retry_after_seconds

session=requests.Session()
session.max_redirects=3
session.headers.update({"User-Agent":USER_AGENTS[0],"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9","Referer":"https://www.linkedin.com/jobs/search"})
started=time.time()
records=[]
wait=8
seen=set()
def probe(endpoint,offset):
    global wait, seen
    if time.time()+wait-started>180:
        return None
    time.sleep(wait)
    params={"keywords":"HSBC","location":"China","distance":50,"pageNum":0,"start":offset,"f_C":"1241"}
    before=time.time()
    try:
        response=session.get(endpoint,params=params,timeout=(10,20))
    except requests.RequestException as exc:
        print(json.dumps({"endpoint":endpoint,"offset":offset,"error":type(exc).__name__}),flush=True)
        return None
    jobs=parse_search(response.text,"HSBC","probe","CN") if response.status_code==200 else []
    ids={j["sourceJobId"] for j in jobs}
    cards=BeautifulSoup(response.text,"html.parser").select("div.base-search-card")
    retry_after=retry_after_seconds(response.headers.get("Retry-After"))
    record={"endpointPath":urlsplit(endpoint).path,"offset":offset,"http":response.status_code,"finalPath":urlsplit(response.url).path,"elapsedSeconds":round(time.time()-before,3),"bytes":len(response.content),"cards":len(cards),"matchingJobs":len(jobs),"newJobs":len(ids-seen),"repeatedJobs":len(ids&seen),"blockedMarkup":block_page(response.text,response.url),"retryAfterSeconds":retry_after}
    if endpoint.endswith("/jobs/search/"):
        seen.update(ids)
    wait=max(60,retry_after or 0) if response.status_code==429 else 8
    response.close()
    records.append(record)
    print(json.dumps(record),flush=True)
    return record
probe("https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",0)
first=probe("https://www.linkedin.com/jobs/search/",0)
if first and first["http"]==200 and first["cards"] and first["matchingJobs"] and not first["blockedMarkup"]:
    probe("https://www.linkedin.com/jobs/search/",first["cards"])
else:
    print("Public search fallback not verified; no pagination assumption made",flush=True)
session.close()
Path("public-search-probe.json").write_text(json.dumps(records,indent=2))
summary=os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary,"a") as handle:
        handle.write("### Public search fallback evidence\n\n")
        handle.write("\n".join("- "+json.dumps(r) for r in records)+"\n")
