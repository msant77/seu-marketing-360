#!/usr/bin/env python3
"""Reproduz um envio do widget contra o backend do alpha-tester para diagnosticar erros (422 etc.).
Uso: python3 tools/diag-feedback.py big|small|path|rect|upload
  big = anexo de ~700 kB em metadata; small = payload mínimo válido (cria um registro de teste)
  upload = fluxo real de anexo: pede o slot de upload, faz o PUT do PNG no bucket e envia o feedback com metadata.anexos
Lê as credenciais do mesmo lugar que o build.py e nunca imprime a chave."""
import json, sys, os, base64, urllib.request, urllib.error, datetime, zlib, struct
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import build  # noqa: E402  (carrega e valida as credenciais; imprime só o nome do projeto)
cfg = build.ALPHA_TESTER
if not cfg['apiKey']: sys.exit('sem credenciais do widget')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def post(body):
    req = urllib.request.Request(cfg['endpoint'] + '/api/v1/feedback', data=json.dumps(body).encode(), method='POST',
        headers={'Content-Type': 'application/json', 'X-API-Key': cfg['apiKey'], 'Origin': 'https://seumarketing360.pages.dev', 'User-Agent': UA})
    try:
        r = urllib.request.urlopen(req, timeout=40); return r.status, r.read().decode()[:600]
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:800]
def png(w, h, rgb=(200, 30, 30)):
    """PNG válido (RGB sólido) gerado sem dependências, para testar o upload."""
    raw = b''.join(b'\x00' + bytes(rgb) * w for _ in range(h))
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
def request(url, data=None, method='POST', headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers={'User-Agent': UA, **(headers or {})})
    try:
        r = urllib.request.urlopen(req, timeout=60); return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
rect = {'x': 10, 'y': 20, 'width': 300, 'height': 120}
base = dict(pageUrl='https://seumarketing360.pages.dev/produtos', type='bug', title='Diagnóstico do widget (teste, pode apagar)',
    description='Envio de teste feito por tools/diag-feedback.py para reproduzir o erro 422. Pode apagar.',
    elementSelector='main > section:nth-of-type(1) h1', elementRect=rect, trackingToken='diagnostico-build-seu-marketing-360',
    metadata={'viewport': {'width': 1440, 'height': 900}, 'userAgent': UA, 'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'source': 'diag', 'hooks': [{'selector': 'main > section:nth-of-type(1) h1', 'rect': rect}]})
mode = sys.argv[1] if len(sys.argv) > 1 else 'big'
body = dict(base)
if mode == 'path':
    body['pageUrl'] = '/produtos'   # o widget manda só o caminho?
elif mode == 'rect':
    body['elementRect'] = {'top': 20, 'left': 10, 'width': 300, 'height': 120}   # rect sem x/y
elif mode == 'upload':
    data = png(160, 80)
    st, out = request(cfg['endpoint'] + '/api/v1/feedback/upload', json.dumps({'filename': 'captura-teste.png', 'contentType': 'image/png', 'size': len(data)}).encode(),
        headers={'Content-Type': 'application/json', 'X-API-Key': cfg['apiKey'], 'Origin': 'https://seumarketing360.pages.dev'})
    if st != 201: sys.exit(f'slot de upload: HTTP {st} {out.decode()[:400]}')
    slot = json.loads(out); print('slot HTTP', st, '| key', slot['key'], '| expira em', slot.get('expiresIn'), 's')
    st, out = request(slot['url'], data, method='PUT', headers=slot.get('headers') or {'Content-Type': 'image/png'})
    if st not in (200, 201): sys.exit(f'PUT no bucket: HTTP {st} {out.decode()[:400]}')
    print('PUT HTTP', st, '|', len(data), 'bytes')
    body['title'] = 'Teste de anexo (pode apagar)'
    body['description'] = 'Envio de teste com captura real pelo tools/diag-feedback.py upload. Pode apagar.'
    body['metadata'] = dict(base['metadata'], anexos=[{'key': slot['key'], 'name': 'captura-teste.png', 'type': 'image/png', 'regionCapture': True}])
elif mode == 'big':
    big = base64.b64encode(os.urandom(520_000)).decode()
    body['metadata'] = dict(base['metadata'], anexos=[{'nome': 'captura.png', 'tipo': 'image/png', 'dataUrl': 'data:image/png;base64,' + big}])
print('modo:', mode, '| payload:', len(json.dumps(body)), 'bytes')
status, text = post(body); print('HTTP', status); print(text)
