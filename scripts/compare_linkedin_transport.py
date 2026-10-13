import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit
import requests

sys.path.insert(0, str(Path("current/scripts/jobspy").resolve()))
from linkedin_http import Coordinator, LinkedInSession, retry_after_seconds
spec = importlib.util.spec_from_file_location("original_search", "original/scripts/jobspy/fetch_linkedin_requests.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)

headers = {"User-Agent": original.USER_AGENTS[0], "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9", "Referer": original.BASE + "/jobs/search"}
pairs = [("HSBC", 0), ("Standard Chartered", 0), ("JPMorgan Chase", 10), ("Citi", 30)]
results = []
started = time.time()
wait = 8
stop = False
with tempfile.TemporaryDirectory() as tmp:
    for pair, (company, offset) in enumerate(pairs):
        modes = ("original", "current") if pair % 2 == 0 else ("current", "original")
        for mode in modes:
            if stop or time.time() + wait - started > 180:
                stop = True
                break
            time.sleep(wait)
            params = {"keywords": company, "location": "China", "distance": 50, "pageNum": 0, "start": offset, "f_C": original.COMPANIES[company]["company_id"]}
            session = requests.Session() if mode == "original" else LinkedInSession(attempts=1, coordinator=Coordinator(Path(tmp)/f"{pair}-{mode}.json", min_interval=0, deadline=time.time()+30), user_agents=original.USER_AGENTS, linear_backoff=True)
            session.headers.update(headers)
            session.max_redirects = 3
            record = {"mode": mode, "company": company, "pageStart": offset}
            response = None
            request_start = time.time()
            try:
                response = session.get(original.SEARCH_URL, params=params, timeout=(10, 20))
            except requests.RequestException as exc:
                response = exc.response
                record["error"] = type(exc).__name__
            record["elapsedSeconds"] = round(time.time()-request_start, 3)
            if response is not None:
                record["http"] = response.status_code
                record["redirectStatuses"] = [r.status_code for r in response.history]
                record["finalPath"] = urlsplit(response.url).path
                record["bytes"] = len(response.content)
                record["retryAfterSeconds"] = retry_after_seconds(response.headers.get("Retry-After"))
                record["matchingJobs"] = len(original.parse_search(response.text, company, "probe", "CN")) if response.status_code == 200 else 0
                if response.status_code == 429:
                    retry_after = record["retryAfterSeconds"]
                    wait = max(60, retry_after or 0)
                    if wait > 180:
                        stop = True
                else:
                    wait = 8
                response.close()
            else:
                record["http"] = 0
                wait = 8
            session.close()
            results.append(record)
            print(json.dumps(record, ensure_ascii=False), flush=True)
        if stop:
            break
report = {"samples": results, "elapsedSeconds": round(time.time()-started, 3), "completePairs": len(results)//2, "stoppedEarly": stop, "scope": "small read-only comparison; not a full crawl"}
Path("transport-comparison.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a") as handle:
        handle.write("### Same-runner original/current transport evidence\n\n")
        handle.write("| Mode | Company | Offset | HTTP | Matching jobs | Seconds |\n|---|---|---:|---:|---:|---:|\n")
        for r in results:
            handle.write(f"| {r['mode']} | {r['company']} | {r['pageStart']} | {r['http']} | {r.get('matchingJobs', 0)} | {r['elapsedSeconds']} |\n")
        handle.write("\nEight requests maximum; honours server waits and a three-minute budget. No canonical data or scraping state is published.\n")
