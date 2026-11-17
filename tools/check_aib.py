"""네이버 AI 브리핑 확인 도구.
사용: python3 -I tools/check_aib.py "키워드1" "키워드2" ...
출력: 키워드별 AI 브리핑 표시 여부(PC), 요약문, 인용 출처 목록(JSON)
"""
import json, re, sys, urllib.parse, urllib.request
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

def fetch(q):
    url = 'https://search.naver.com/search.naver?query=' + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ko-KR,ko;q=0.9'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')

def blocks(h):
    for m in re.finditer(r'entry\.bootstrap\(document\.getElementById\("[^"]+"\),\s*', h):
        try:
            yield json.JSONDecoder().raw_decode(h, m.end())[0]
        except Exception:
            pass

def sources(o, acc):
    if isinstance(o, dict):
        if 'url' in o and ('title' in o or 'sourceName' in o) and ('platform' in o or 'sourceName' in o):
            acc.append({k: o.get(k, '') for k in ('platform', 'sourceName', 'title', 'url', 'dateText')})
        for v in o.values(): sources(v, acc)
    elif isinstance(o, list):
        for v in o: sources(v, acc)

def check(q):
    res = {'keyword': q, 'ai_briefing': False, 'summary': '', 'sources': []}
    try:
        h = fetch(q)
    except Exception as e:
        res['error'] = str(e); return res
    for b in blocks(h):
        if 'ai-briefing' in (b.get('refs') or {}).get('blockId', ''):
            res['ai_briefing'] = True
            res['summary'] = (((b.get('body') or {}).get('props') or {}).get('summary') or {}).get('copy', '')
            acc = []; sources(b, acc)
            seen = set()
            for s in acc:
                if s['url'] not in seen:
                    seen.add(s['url']); res['sources'].append(s)
    res['our_site_cited'] = any('geukdeal.github.io' in s['url'] for s in res['sources'])
    return res

if __name__ == '__main__':
    print(json.dumps([check(q) for q in sys.argv[1:]], ensure_ascii=False, indent=1))
