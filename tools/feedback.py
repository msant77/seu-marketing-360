#!/usr/bin/env python3
"""CLI provisório para o feedback do alpha-tester (projeto do site), usando a sessão do painel.
A sessão (valor do cookie __Secure-authjs.session-token de https://dev.alphatester.app) fica em ../alpha-tester.session,
um nível acima do repositório, fora do git. Nunca é impressa.

Uso:
  python3 tools/feedback.py list [--status new|triaged|accepted|rejected|in_progress|resolved|shipped] [--all]
  python3 tools/feedback.py show ID
  python3 tools/feedback.py set ID STATUS [--note "texto"] [--priority low|medium|high|critical]
  python3 tools/feedback.py issue ID          # cria a issue no GitHub pela integração do projeto
  python3 tools/feedback.py attachment KEY    # baixa um anexo pelo proxy do painel e confere tipo e tamanho
"""
import json, os, sys, urllib.request, urllib.error, urllib.parse, textwrap
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import build  # noqa: E402  (endpoint + projectId validados; imprime só o nome do projeto)
cfg = build.ALPHA_TESTER
HERE = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(HERE, '..', '..', 'alpha-tester.session')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

def session():
    try:
        tok = open(SESSION_FILE, encoding='utf-8').read().strip()
    except FileNotFoundError:
        sys.exit(f'sessão não encontrada: salve o valor do cookie __Secure-authjs.session-token em {os.path.normpath(SESSION_FILE)}')
    if not tok: sys.exit('arquivo de sessão vazio')
    return tok

def call(method, path, body=None, params=None):
    url = cfg['endpoint'] + path + ('?' + urllib.parse.urlencode(params) if params else '')
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Cookie': '__Secure-authjs.session-token=' + session(), 'User-Agent': UA,
        'Accept': 'application/json', **({'Content-Type': 'application/json'} if data else {})})
    try:
        with urllib.request.urlopen(req, timeout=40) as r: return r.status, json.loads(r.read().decode() or 'null')
    except urllib.error.HTTPError as e:
        txt = e.read().decode()[:400]
        if e.code == 401: sys.exit('401: sessão inválida ou expirada. Copie o cookie de novo.')
        try: return e.code, json.loads(txt)
        except Exception: return e.code, {'error': txt}

P = f"/api/v1/projects/{cfg['projectId']}/feedback"
def cmd_list(args):
    params = {'limit': 100, 'page': 1}
    if '--status' in args: params['status'] = args[args.index('--status') + 1]
    st, d = call('GET', P, params=params)
    if st != 200: sys.exit(f'HTTP {st}: {d}')
    items = d.get('items') or d.get('feedback') or d.get('data') or []
    print(f"{len(items)} de {d.get('total', len(items))} feedback(s)\n")
    for it in items:
        page = (it.get('pageUrl') or '').replace('https://seumarketing360.pages.dev', '') or '/'
        rep = it.get('reporterName') or it.get('reporterEmail') or (it.get('reporterId') or '')[:8]
        print(f"{it['id'][:8]}  {it.get('createdAt','')[:16]}  {it.get('type',''):<11} {it.get('status',''):<11} {page:<22} {rep}")
        print(f"          {it.get('title','')}")
        if '--all' in args:
            print(textwrap.indent(textwrap.fill(it.get('description') or '', 100), '          '))
            if it.get('elementSelector'): print(f"          elemento: {it['elementSelector'][:120]}")
        print()

def resolve(prefix):
    st, d = call('GET', P, params={'limit': 100})
    if st != 200: sys.exit(f'HTTP {st}: {d}')
    m = [it for it in (d.get('items') or d.get('feedback') or d.get('data') or []) if it['id'].startswith(prefix)]
    if len(m) != 1: sys.exit(f'{len(m)} feedback(s) com prefixo {prefix}')
    return m[0]

def cmd_show(args):
    it = resolve(args[0]); print(json.dumps(it, ensure_ascii=False, indent=2)[:4000])

def cmd_set(args):
    it = resolve(args[0]); body = {'status': args[1]}
    if '--note' in args: body['note'] = args[args.index('--note') + 1]
    if '--priority' in args: body['priority'] = args[args.index('--priority') + 1]
    st, d = call('PATCH', f"{P}/{it['id']}", body=body); print(f"HTTP {st}", json.dumps(d, ensure_ascii=False)[:400])

def cmd_issue(args):
    it = resolve(args[0]); st, d = call('POST', f"{P}/{it['id']}/github-issue"); print(f"HTTP {st}", json.dumps(d, ensure_ascii=False)[:400])

def cmd_attachment(args):
    url = cfg['endpoint'] + '/api/v1/attachments/' + urllib.parse.quote(args[0], safe='/')
    req = urllib.request.Request(url, headers={'Cookie': '__Secure-authjs.session-token=' + session(), 'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read(); kind = 'PNG' if data[:8] == b'\x89PNG\r\n\x1a\n' else 'outro'
            print(f"HTTP {r.status} {r.headers.get('Content-Type')} {len(data)} bytes ({kind}); cache: {r.headers.get('Cache-Control')}")
    except urllib.error.HTTPError as e: print(f'HTTP {e.code}', e.read().decode()[:300])

if __name__ == '__main__':
    a = sys.argv[1:]
    {'list': cmd_list, 'show': cmd_show, 'set': cmd_set, 'issue': cmd_issue, 'attachment': cmd_attachment}.get(a[0] if a else '', lambda _: sys.exit(__doc__))(a[1:])
