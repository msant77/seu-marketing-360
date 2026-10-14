#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o site Seu Marketing 360 (4 páginas + privacidade) a partir dos textos da Juliana (rodada 7, 14/10/2026).
Uso: python3 build.py [--base https://url] [--noindex]
Saída: out/dist/ (site completo para hospedagem) e out/artifact/ (index sem esqueleto + páginas + img, para o artifact).
Dados que ainda faltam (WhatsApp, Hotmart, agenda): preencher nas constantes abaixo e rodar de novo."""
import os, re, shutil, sys, datetime, html, json
from urllib.parse import quote
HERE=os.path.dirname(os.path.abspath(__file__))
BASE='https://seumarketing360.com.br'; NOINDEX=False
a=sys.argv[1:]
if '--base' in a: BASE=a[a.index('--base')+1].rstrip('/')
if '--noindex' in a: NOINDEX=True

WHATSAPP_NUMBER=''          # ex.: '5511999999999' (DDI+DDD+número, só dígitos)
HOTMART_RECEITA='#'         # link do curso Receita de Bolo na Hotmart
HOTMART_VIDEO='#'           # link do curso Captação e Edição de Vídeos
AGENDA_ONLINE='#'           # link de agenda da reunião online (Cal.com) ou de pagamento
AGENDA_PRESENCIAL='#'       # idem, presencial
INSTAGRAM='https://www.instagram.com/julianaarv'
# Widget de feedback (alpha-tester). Vazio = desligado. Quando ligado, só aparece em *.pages.dev ou com localStorage.alpha = '1'.
ALPHA_TESTER={'endpoint':'','projectId':'','apiKey':''}
# Credenciais do widget ficam UM NÍVEL ACIMA do repositório (fora do git): ../.env.local ou ../alpha-tester.local,
# ou nas variáveis de ambiente ALPHA_TESTER_ENDPOINT / ALPHA_TESTER_PROJECT_ID / ALPHA_TESTER_API_KEY.
# O nome da variável no arquivo não importa: o script usa o valor que começa com at_pub_ (chave publicável; uma at_sec_ é ignorada),
# um UUID como projectId e um endereço https com "alphatester" como endpoint. Sem projectId, pergunta ao backend.
def _load_alpha():
    uuid_re=re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',re.I)
    env=os.environ
    for key,var in (('endpoint','ALPHA_TESTER_ENDPOINT'),('projectId','ALPHA_TESTER_PROJECT_ID'),('apiKey','ALPHA_TESTER_API_KEY')):
        if env.get(var): ALPHA_TESTER[key]=env[var].strip()
    for name in ('.env.local','alpha-tester.local'):
        f=os.path.join(HERE,'..',name)
        if not os.path.exists(f): continue
        for line in open(f,encoding='utf-8'):
            line=line.strip()
            if line.startswith('export '): line=line[7:]
            if not line or line.startswith('#') or '=' not in line: continue
            k,_,v=line.partition('='); k=k.strip(); v=v.strip().strip('"').strip("'")
            if k=='ALPHA_TESTER_ENDPOINT': ALPHA_TESTER['endpoint']=v
            elif k=='ALPHA_TESTER_PROJECT_ID': ALPHA_TESTER['projectId']=v
            elif k=='ALPHA_TESTER_API_KEY': ALPHA_TESTER['apiKey']=v
            elif v.startswith('at_pub_') and not ALPHA_TESTER['apiKey']: ALPHA_TESTER['apiKey']=v
            elif uuid_re.match(v) and not ALPHA_TESTER['projectId']: ALPHA_TESTER['projectId']=v
            elif v.startswith('http') and 'alphatester' in v and not ALPHA_TESTER['endpoint']: ALPHA_TESTER['endpoint']=v.rstrip('/')
    k=ALPHA_TESTER['apiKey']
    if not k: return
    if not k.startswith('at_pub_'): sys.exit('A chave do widget precisa ser a publicável (at_pub_...). Uma chave secreta nunca vai para o HTML.')
    if not ALPHA_TESTER['endpoint']: ALPHA_TESTER['endpoint']='https://dev.alphatester.app'
    import urllib.request
    try:
        req=urllib.request.Request(ALPHA_TESTER['endpoint']+'/api/v1/sdk/init',headers={'X-API-Key':k,'Origin':'https://seumarketing360.pages.dev','User-Agent':'Mozilla/5.0 (Macintosh) seu-marketing-360-build/1.0'})
        info=json.load(urllib.request.urlopen(req,timeout=20))
    except Exception as e:
        sys.exit(f'Widget: backend não validou a chave ({e}). Nada publicado com o widget.')
    if not ALPHA_TESTER['projectId']: ALPHA_TESTER['projectId']=info.get('projectId','')
    if ALPHA_TESTER['projectId']!=info.get('projectId'): sys.exit('Widget: o projectId do arquivo não bate com o da chave.')
    print(f"widget alpha-tester: projeto {info.get('projectName')} ({info.get('projectSlug')}) em {ALPHA_TESTER['endpoint']}")
_load_alpha()
EMAIL='contato@seumarketing360.com.br'
def wa(msg):
    return f'https://wa.me/{WHATSAPP_NUMBER}?text={quote(msg)}' if WHATSAPP_NUMBER else 'produtos.html#contato'

def ic(paths, cls='ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
I={
 'arrow':'<path d="M7 17 17 7M8 7h9v9"/>',
 'people':'<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 14.5c3 0 6 1.5 6 5.5"/>',
 'heart':'<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
 'share':'<circle cx="6" cy="12" r="2.6"/><circle cx="18" cy="6" r="2.6"/><circle cx="18" cy="18" r="2.6"/><path d="m8.4 10.8 7.2-3.6M8.4 13.2l7.2 3.6"/>',
 'box':'<path d="M12 3 4 7v10l8 4 8-4V7z"/><path d="M4 7l8 4 8-4M12 11v10"/>',
 'target':'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r=".8"/>',
 'db':'<ellipse cx="12" cy="5.5" rx="7.5" ry="2.8"/><path d="M4.5 5.5v13c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8v-13"/><path d="M4.5 12c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8"/>',
 'search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5M8 10.5l1.8 1.8 3.4-3.6"/>',
 'doc':'<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
 'cal':'<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4M9 14.5l2 2 4-4"/>',
 'ig':'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>',
 'speaker':'<path d="M3 11v3l12 5V6L3 11zM15 9a4 4 0 0 1 0 6"/>',
 'bars':'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
 'plus':'<path d="M12 3v5M12 16v5M3 12h5M16 12h5"/>',
}
ARROW=f'<i class="ar">{ic(I["arrow"], cls="")}</i>'
FONTS='<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500&family=Big+Shoulders+Display:wght@800&display=swap" rel="stylesheet">'
CSS=open(os.path.join(HERE,'style.css'),encoding='utf-8').read()+'\n.pol p,.pol li{max-width:65ch}.pol h2{margin-top:28px}.pol ul{padding-left:20px}\n'
SCENE='<div class="scene" aria-hidden="true"><i></i><i></i><i></i></div>'
FX=('<div class="fx" aria-hidden="true">'
 f'<div class="pl" data-s="0.1" style="left:5%;top:14%"><div class="bub" style="--z:60px;--t:9s;--dl:0s">{ic(I["speaker"])}</div></div>'
 '<div class="pl" data-s="0.16" style="left:87%;top:20%"><div class="bub" style="--z:48px;--t:11s;--dl:1s"></div></div>'
 f'<div class="pl" data-s="0.09" style="left:7%;top:58%"><div class="bub" style="--z:64px;--t:10s;--dl:0.4s">{ic(I["bars"])}</div></div>'
 f'<div class="pl" data-s="0.2" style="left:89%;top:64%"><div class="bub" style="--z:50px;--t:8s;--dl:2s">{ic(I["plus"])}</div></div>'
 '<div class="pl" data-s="0.28" style="left:48%;top:88%"><div class="bub" style="--z:36px;--t:12s;--dl:1s"></div></div></div>')
NAV=[('index.html','Página Inicial'),('quem-eu-sou.html','Quem eu sou'),('marcas-e-creators.html','Marcas & Creators'),('produtos.html','Produtos')]
def header(cur):
    links=''.join(f'<a href="{h}"{" aria-current=\"page\"" if h==cur else ""}>{html.escape(t)}</a>' for h,t in NAV)
    links+=f'<a class="ig" href="{INSTAGRAM}" target="_blank" rel="noopener">{ic(I["ig"], cls="")}@julianaarv</a>'
    links+=f'<a class="btn" href="{wa("Olá, Juliana! Quero falar sobre o meu negócio.")}">Falar com a Juliana</a>'
    return (f'<header class="top glass dg"><a class="brand" href="index.html"><span>Seu Marketing 360°</span><small>por Juliana Aragão</small></a>'
            f'<nav id="nav">{links}</nav><button class="menu" type="button" aria-expanded="false" aria-controls="nav">Menu</button></header>')
FOOTER=(f'<footer class="glass dg">Seu Marketing 360 · por Juliana Aragão · {EMAIL} · <a href="{INSTAGRAM}" target="_blank" rel="noopener">@julianaarv</a> · '
        '<a href="privacidade.html">Política de privacidade</a></footer>')
JS_COMMON="""<script>
(function(){if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;var e=[].slice.call(document.querySelectorAll('.pl'));function u(){var y=window.scrollY;e.forEach(function(n){n.style.setProperty('--py',(-y*n.dataset.s)+'px')})}addEventListener('scroll',u,{passive:true});u()})();
(function(){if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;var e=[].slice.call(document.querySelectorAll('.s3w'));function u(){var y=window.scrollY;e.forEach(function(n){n.style.setProperty('--sy',Math.sin(y/350)*300)})}addEventListener('scroll',u,{passive:true});u()})();
(function(){var b=document.querySelector('.menu'),n=document.getElementById('nav');if(!b||!n)return;b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false')})})();
</script>"""
JS_LENS="""<script>
(function(){var s=document.querySelector('.sph'),c=document.querySelector('.scene-copy'),l=document.querySelector('.lens');if(!s||!c||!l)return;var raf=0;function place(){raf=0;var r=s.getBoundingClientRect();c.style.width=innerWidth+'px';c.style.height=innerHeight+'px';c.style.left=(-r.left)+'px';c.style.top=(-r.top)+'px';c.style.transformOrigin=(r.left+r.width/2)+'px '+(r.top+r.height/2)+'px';l.style.visibility='visible'}function req(){if(!raf)raf=requestAnimationFrame(place)}addEventListener('scroll',req,{passive:true});addEventListener('resize',req);place();setTimeout(place,300)})();
</script>"""
def widget():
    if not all(ALPHA_TESTER.values()): return ''
    return ('<script src="/js/alpha-tester.umd.js" defer></script>\n<script>addEventListener("DOMContentLoaded",function(){var on=/\\.pages\\.dev$/.test(location.hostname)||localStorage.getItem("alpha")==="1";'
            'if(on&&window.AlphaTester)AlphaTester.init('+json.dumps(ALPHA_TESTER)+')});</script>\n')
def cta(primary_href, primary='Começar os 30 dias', alt=True):
    s=f'<div class="cta"><a class="btn" href="{primary_href}">{primary}</a>'
    if alt: s+=f'<a class="btn alt" href="{wa("Olá, Juliana! Tenho uma dúvida sobre o Seu Marketing 360.")}">Tirar dúvidas no WhatsApp</a>'
    return s+'</div>'
def s3w(img, cls): return f'<div class="s3w {cls}"><img src="img/{img}" alt="" aria-hidden="true"></div>'
chips=[('people','Equipe'),('heart','Cliente'),('share','Redes'),('box','Entrega'),('target','Concorrência')]
ORBIT=('<div class="orbit" role="img" aria-label="Seu negócio no centro, cercado por equipe, cliente, redes, entrega e concorrência"><div class="path"></div><div class="spin">'
 +''.join(f'<div class="chip" style="--a:{i*72}deg"><span>{ic(I[k])}{t}</span></div>' for i,(k,t) in enumerate(chips))+'</div><div class="core">seu<br>negócio</div></div>')
WIN=('<div class="win"><div class="sph"><div class="lens"><div class="scene scene-copy" aria-hidden="true"><i></i><i></i><i></i></div></div></div>'
 '<div class="gy"><img src="img/3d-giroscopio.webp" alt="" aria-hidden="true"></div>'
 '<div class="wb" aria-hidden="true"><span class="bub" style="--z:54px;--t:10s;--dl:.3s;left:6%;top:9%"></span><span class="bub" style="--z:30px;--t:8s;--dl:1.4s;right:9%;top:15%"></span><span class="bub" style="--z:66px;--t:12s;--dl:.8s;right:5%;bottom:8%"></span><span class="bub" style="--z:24px;--t:9s;--dl:2s;left:12%;bottom:13%"></span></div>'
 +ORBIT+'</div>')

# ---------- Página Inicial ----------
HOME=f'''<main><section class="sec"><div class="panel glass hero2">
<div class="numrow"><div class="num" aria-hidden="true">360</div>
<div class="specs"><p><b>Serviço</b>Marketing 360º de forma individual, personalizada e acessível.</p><p><b>Frentes</b>Posicionamento de marca, estratégia, redes sociais, tráfego pago, produção audiovisual, presença digital e geração de oportunidades comerciais.</p><p><b>Formato</b>Método Experimental 30: trinta dias de acompanhamento e um relatório no fim. Depois, trimestral, semestral ou anual.</p></div></div>
<div class="copy2"><h1>Seu negócio inteiro bem posicionado nas redes.</h1>
<p>Aqui você não precisa esperar de 3 a 6 meses para ver o resultado do nosso trabalho. Nosso plano experimental permite 30 dias de acompanhamento e, ao final dos 30 dias, nossa equipe envia um relatório com os resultados e tudo que trabalhamos de forma clara e objetiva.</p>
<p>Sem contratos de 1 ano que te prendem a uma agência sem conhecer o trabalho que ela oferece. Sem multas abusivas. Sem ficar preso a uma empresa que não te faz alcançar os resultados desejados. Atendimento personalizado de forma acessível.</p>
<div class="cta"><a class="btn w" href="produtos.html#metodo30">Começar os 30 dias{ARROW}</a><a class="btn alt" href="{wa("Olá, Juliana! Tenho uma dúvida sobre o Seu Marketing 360.")}">Tirar dúvidas no WhatsApp</a></div></div>
{s3w("3d-barras.webp","s-bars")}</div></section>
<div class="duo"><aside class="mini glass dg"><small>Curso online · 8 módulos · 19 aulas</small><h3>Receita de Bolo</h3><small>O passo a passo do método para aplicar no seu negócio.</small><span class="v">R$ 39,90</span><a class="mag" href="produtos.html#adicionais" aria-label="Ver o curso Receita de Bolo">{ic(I["arrow"], cls="")}</a></aside>
{WIN}</div>
<div class="bar glass dg"><span class="th"></span><div class="tt">Novo · Método Experimental 30<small>R$ 2.497,79 · trinta dias dentro da sua empresa, com relatório no fim</small></div><a class="go" href="produtos.html#metodo30" aria-label="Ver o Método Experimental 30">{ic(I["arrow"], cls="")}</a></div>

<section class="sec" id="oque"><div class="panel glass prose">{s3w("3d-alvo.webp","s-tg")}
<h2>O que é o Marketing 360º?</h2>
<p class="lead">Marketing 360º vai muito além das redes sociais. Sua empresa não precisa apenas aparecer, precisa crescer com estratégia.</p>
<p>Diferente do marketing tradicional, focado principalmente na gestão de redes sociais e na produção de conteúdo, o Marketing 360° conecta todas as frentes da comunicação e do marketing do seu negócio:</p>
<div class="tags"><span>Posicionamento de marca</span><span>Estratégia</span><span>Redes sociais</span><span>Tráfego pago</span><span>Produção audiovisual</span><span>Presença digital</span><span>Geração de oportunidades comerciais</span></div>
<p>Tudo funciona de forma integrada, com ações planejadas para fortalecer sua marca, atrair o público certo e criar oportunidades reais de crescimento.</p>
<p>Mais do que contratar serviços isolados, você conta com uma visão estratégica do seu negócio, em que cada ação tem um propósito e contribui para seus objetivos.</p>
<div class="card hl" style="margin-top:22px;gap:16px"><p class="quote">Sua empresa merece mais do que presença digital. Merece uma estratégia completa para crescer.</p>{cta("produtos.html#metodo30")}</div>
</div></section></main>'''

# ---------- Quem eu sou ----------
BIO=f'''<main><section class="sec"><div class="panel glass pg prose">{s3w("3d-giroscopio.webp","s-tg")}
<small class="kicker">Quem eu sou</small>
<h1>Prazer, sou Juliana Aragão S.</h1>
<p class="lead">Marketing não é apenas estar presente. É construir uma presença que faça sentido para o seu negócio.</p>
<p>Trabalho há mais de 11 anos com redes sociais e marketing, desenvolvendo estratégias de conteúdo, posicionamento de marca e comunicação para diferentes projetos e segmentos.</p>
<p>Ao longo dessa trajetória, compreendi que o desafio de uma empresa vai muito além de publicar nas redes sociais. É preciso entender o negócio, conhecer o público, identificar oportunidades e conectar cada ação de marketing a objetivos reais.</p>
<p>Minha experiência inclui a gestão de marketing, o planejamento estratégico, a análise de métricas, a direção criativa e a produção audiovisual. Já atuei na liderança de equipes e no desenvolvimento de estratégias de comunicação, unindo visão analítica e execução para transformar ideias em ações consistentes.</p>
<p>Foi essa visão que fortaleceu minha forma de trabalhar: o marketing precisa funcionar como um sistema integrado, e não como um conjunto de ações isoladas.</p>
<p>É por isso que acredito no marketing 360°. Uma abordagem que considera a empresa como um todo, conecta seus canais de comunicação e alinha estratégia, criatividade e execução para construir uma marca mais forte, relevante e competitiva.</p>
<p>Meu objetivo é ajudar micro, pequenas e médias empresas a enxergarem o marketing como parte estratégica do negócio, com planejamento, clareza e ações coerentes com sua realidade e seus objetivos.</p>
<p>Porque sua empresa não precisa apenas aparecer mais. Precisa comunicar melhor seu valor, conquistar a confiança das pessoas certas e construir bases consistentes para crescer.</p>
<div class="card hl" style="margin-top:22px"><p class="quote">Estratégia para direcionar. Criatividade para conectar. Marketing para impulsionar o negócio.</p></div>
<div class="cta" style="margin-top:22px"><a class="btn" href="marcas-e-creators.html">Ver marcas e creators{ARROW}</a><a class="btn alt" href="produtos.html">Ver os produtos</a></div>
</div></section></main>'''

# ---------- Marcas & Creators ----------
def names(*ns): return '<div class="names">'+''.join(f'<span>{n}</span>' for n in ns)+'</div>'
MARCAS=f'''<main><section class="sec"><div class="panel glass pg prose">
<small class="kicker">Marcas &amp; Creators</small>
<h1>Marcas, creators e projetos que fazem parte da minha trajetória</h1>
<p class="lead">Mais de 11 anos transformando objetivos de comunicação em estratégias, conteúdo e posicionamento de marca.</p>
<p>Ao longo da minha trajetória, trabalhei com creators, empresas, agências e marcas de diferentes segmentos, desenvolvendo projetos que vão da criação de conteúdo à gestão estratégica de marketing.</p>
<p>Essa experiência me permitiu compreender diferentes públicos, adaptar a comunicação a cada mercado e atuar em frentes que se complementam: branding, produção audiovisual, planejamento editorial, influência digital, parcerias comerciais e análise de desempenho.</p>
<p>Entre os projetos da minha trajetória estão nomes como José Roberto Marques, IBC Coaching, Fernanda Chaud, Chaud Academy, Gabriel Paldim, New Look Time, G-Shock Store, Itaipava, Itubaína, Baw Clothing e WeCreate, além de outros creators, empresas e negócios.</p>
<p>Cada projeto trouxe um desafio específico e ampliou minha visão sobre como construir uma comunicação coerente com a identidade da marca, fortalecer sua presença digital e aproximá-la do público certo.</p>
<p>Mais do que produzir conteúdo, meu trabalho é entender o objetivo por trás de cada ação e transformar estratégia em execução.</p>
</div></section>
<section class="sec"><div class="panel glass"><h2>Marcas e creators em destaque</h2>
<div class="grid" style="margin-top:18px">
<div class="card"><small class="kicker">Autoridade, educação e desenvolvimento humano</small><h3>Marcas pessoais e negócios de conhecimento</h3>{names("José Roberto Marques","IBC Coaching","Fernanda Chaud","Chaud Academy")}<p>Projetos envolvendo produção audiovisual, cobertura de eventos, conteúdo para redes sociais e construção de credibilidade digital.</p></div>
<div class="card"><small class="kicker">Varejo, produtos e negócios</small><h3>Comunicação de marca e objetivos comerciais</h3>{names("New Look Time","G-Shock Store","Itaipava","Itubaína","BaW Clothing","WeCreate")}<p>Experiência com conteúdo de marca, comunicação promocional, campanhas, calendário editorial e estratégias voltadas ao posicionamento e à conexão com consumidores.</p></div>
<div class="card"><small class="kicker">Creators, serviços e marcas pessoais</small><h3>Conteúdo, influência e posicionamento digital</h3>{names("Gabriel Paldim e Studio Gabriel Paldim","Gabi Morretti","Mundo Setti","Giana Mello","Luisa Badaui","Nicole Cell","Ísis Decorações","We Are Family Pet","Mia (projeto de bronzeamento artificial)")}<p>Projetos com diferentes públicos e propostas de valor, incluindo estratégias de conteúdo, identidade visual, produção audiovisual e direcionamento de comunicação.</p></div>
</div>
<div class="card hl wide case" style="margin-top:14px"><small class="kicker">Em destaque · Varejo · Posicionamento · Parcerias · Estratégia comercial</small><h2>New Look Time: da credibilidade digital à estratégia comercial</h2>
<p>O projeto começou com o desafio de fortalecer a credibilidade da marca nas redes sociais, em um mercado no qual a confiança é decisiva para a compra.</p>
<p>A estratégia inicial priorizou conteúdos educativos e vídeos de alerta sobre golpes digitais. Em uma segunda etapa, com a queda das vendas da unidade do Shopping West Plaza, o direcionamento passou a incluir parcerias com o shopping, podcasts, influenciadores e conteúdos que reforçassem a confiança e os diferenciais da loja.</p>
<div class="numrow" style="margin:10px 0;justify-content:flex-start"><div class="big">4<small>meses</small></div><p style="max-width:40ch">Ao final desse período, a loja passou a faturar, em média, o mesmo que as outras unidades.</p></div>
<p>O que esse projeto demonstra: a capacidade de adaptar a estratégia ao momento do negócio, conectar comunicação e ações comerciais e trabalhar com objetivos que vão além das métricas das redes sociais.</p></div>
</div></section>
<section class="sec"><div class="panel glass prose"><h2>Experiência que vai além das redes sociais.</h2>
<p>Cada marca com que trabalhei ampliou minha capacidade de enxergar o marketing de forma integrada: entender o negócio, identificar oportunidades, definir prioridades e transformar objetivos em ações.</p>
<p>É essa visão que levo para cada projeto. Porque uma empresa não precisa apenas aparecer nas redes sociais. Precisa construir confiança, comunicar seus diferenciais e criar caminhos para crescer de forma consistente.</p>
<p class="quote" style="margin-top:18px">Estratégia para direcionar. Criatividade para diferenciar. Execução para transformar planos em ações.</p>
<div style="margin-top:22px">{cta("produtos.html#metodo30")}</div></div></section></main>'''

# ---------- Produtos ----------
def step(k,h,t,dl=''): return f'<div class="card"><span class="ico"{(" style=\"--dl:"+dl+"\"") if dl else ""}>{ic(I[k])}</span><h3>{h}</h3><p>{t}</p></div>'
STEPS=(step('db','Dias 1 a 30: dentro do seu negócio','Três reuniões por semana, de até duas horas. A gente analisa o CRM da sua empresa, ou instala um se você ainda não tem, e acompanha o atendimento de perto.')
 +step('search','Diagnóstico preciso','Em que momento os seus clientes param de responder, a eficácia da sua equipe e como ativar a base de leads que você já tem.','.6s')
 +step('doc','Dia 30: relatório na sua mão','Tudo que foi trabalhado na sua empresa e o diagnóstico do seu CRM, num PDF claro e objetivo, para guardar e aplicar.','1.2s')
 +step('cal','Você decide como seguir','Método Trimestral, Semestral ou Anual, ou encerra por aqui. Contrato maleável: cancelamento com 30 dias de antecedência; no semestral e no anual, depois dos três primeiros meses.','1.8s'))
INCLUI='<li>Acompanhamento dentro da sua empresa</li><li>Olhar 360° para o seu negócio e as suas redes sociais</li><li>Acompanhamento do CRM</li><li>1 reunião semanal online de até 3 horas</li><li>Branding e identidade visual das suas redes sociais</li><li>Direcionamento de conteúdo para as mídias sociais</li><li>Acompanhamento e feedback de postagens</li><li>Contrato maleável</li>'
def plan(dur,nome,parc,avista,itens,msg):
    return (f'<div class="card"><small>{dur}</small><h3>{nome}</h3><span class="v">{parc}</span><small>ou {avista} à vista</small><ul>'+''.join(f'<li>{i}</li>' for i in itens)+f'</ul><a class="btn" href="{wa(msg)}">Quero este método</a></div>')
PRODUTOS=f'''<main><section class="sec"><div class="panel glass pg">{s3w("3d-alvo.webp","s-tg")}<small class="kicker">Produtos</small><h1>Comece pelos 30 dias ou escolha o seu método.</h1>
<p class="lead">O Método Experimental 30 é a porta de entrada: trinta dias dentro da sua empresa, do CRM ao Instagram, e um relatório claro no fim. Depois, você decide se segue no trimestral, no semestral ou no anual.</p>
<div class="grid" id="metodo30">{STEPS}</div>
<p class="fine">Como a gente sabe que está funcionando? A sua própria equipe pergunta, todo dia, para quem chega na loja: por onde você chegou até a gente?</p></div></section>

<section class="sec" id="metodos"><div class="panel glass"><h2>Métodos</h2>
<div class="grid" style="margin-top:18px"><div class="card hl wide"><small>Produto principal · 30 dias</small><h3>Método Experimental 30</h3><p>Trinta dias com uma especialista dentro da sua empresa, do CRM ao Instagram.</p>
<ul><li>Olhar 360° para o seu negócio e as suas redes sociais</li><li>Análise do CRM da sua empresa, ou instalação de um CRM se você ainda não usa</li><li>3 reuniões por semana, de até 2 horas</li><li>Branding e identidade visual das suas redes sociais</li><li>Direcionamento de conteúdo para as mídias sociais</li><li>No dia 30, um PDF com todo o trabalho feito e o diagnóstico do seu CRM</li></ul>
<span class="v">R$ 2.497,79</span><small>30 dias · pagamento único · sem fidelidade · depois, Método Trimestral, Semestral ou Anual</small><a class="btn" href="{wa("Olá, Juliana! Quero começar o Método Experimental 30.")}">Começar os 30 dias</a></div>
{plan("3 meses","Método Trimestral","3x R$ 1.997,79","R$ 5.397,79",["Relatório quinzenal do CRM","1 visita presencial de até 5 horas","Curso de edição de vídeo para até 2 pessoas da equipe","Cancelamento com 30 dias de antecedência"],"Olá, Juliana! Quero saber mais sobre o Método Trimestral.")}
{plan("6 meses","Método Semestral","6x R$ 1.797,79","R$ 10.397,79",["Relatório quinzenal do CRM","1 visita presencial por mês, de até 5 horas","Curso de edição de vídeo para até 2 pessoas da equipe","Depois de 3 meses, cancelamento com 30 dias de antecedência"],"Olá, Juliana! Quero saber mais sobre o Método Semestral.")}
{plan("12 meses","Método Anual","12x R$ 1.597,79","R$ 18.097,79",["Relatório semanal do CRM","1 visita presencial a cada 15 dias, de até 5 horas","Curso de edição de vídeo para até 10 pessoas da equipe","Receita de Bolo para até 5 pessoas da equipe","Treinamento de Atendimento, método da rede Outback","3 artes no Canva por mês","1 Mídia Kit / Portfólio","Depois de 3 meses, cancelamento com 30 dias de antecedência"],"Olá, Juliana! Quero saber mais sobre o Método Anual.")}
<div class="card wide"><h3>Todo método inclui</h3><ul>{INCLUI}</ul></div></div></div></section>

<section class="sec" id="adicionais"><div class="panel glass"><h2>Adicionais</h2>
<div class="grid" style="margin-top:18px"><div class="card"><h3>Treinamento de Atendimento</h3><p>1 dia presencial, até 10 pessoas, com o método de conexão usado em toda a rede Outback (Outback Steakhouse, Abbraccio e Aussie Grill): entender a necessidade do cliente, oferecer o produto ou serviço certo e descobrir por onde ele chegou até você.</p><span class="v">R$ 499,99</span><a class="btn" href="{wa("Olá, Juliana! Quero saber mais sobre o Treinamento de Atendimento.")}">Pedir pelo WhatsApp</a></div>
<div class="card"><h3>Mídia Kit / Portfólio</h3><p>PDF de apresentação dos seus produtos e serviços.</p><span class="v">R$ 499,99</span><a class="btn" href="{wa("Olá, Juliana! Quero um Mídia Kit / Portfólio.")}">Pedir pelo WhatsApp</a></div>
<div class="card"><h3>3 Artes Canva</h3><p>3 artes em carrossel para as suas redes.</p><span class="v">R$ 349,99</span><a class="btn" href="{wa("Olá, Juliana! Quero as 3 artes no Canva.")}">Pedir pelo WhatsApp</a></div>
<div class="card"><small>Curso online · 8 módulos · 19 aulas</small><h3>Receita de Bolo</h3><p>Oito módulos para você adquirir o olhar técnico de estrategista: identificar os pontos fortes e fracos do seu negócio e posicioná-lo nas redes. A receita é minha; as habilidades de confeiteira você desenvolve.</p><span class="v">R$ 39,90</span><a class="btn" href="{HOTMART_RECEITA}">Comprar na Hotmart</a></div>
<div class="card"><small>Mini-curso · 3 módulos · 6 aulas</small><h3>Captação e Edição de Vídeos (básico)</h3><p>Para a sua equipe gravar e editar na pronta entrega.</p><span class="v">R$ 19,90</span><a class="btn" href="{HOTMART_VIDEO}">Comprar na Hotmart</a></div></div></div></section>

<section class="sec" id="contato"><div class="panel glass"><h2>Fale com a especialista</h2>
<div class="grid" style="margin-top:18px"><div class="card"><small>Grátis</small><h3>Dúvidas pelo WhatsApp Business</h3><p>Me chama por texto ou áudio, do seu jeito. Tire as suas dúvidas por lá, sem custo.</p><a class="btn" href="{wa("Olá, Juliana! Tenho uma dúvida sobre o Seu Marketing 360.")}">Abrir o WhatsApp</a></div>
<div class="card"><small>Google Meet · 1 hora</small><h3>Reunião online</h3><span class="v">R$ 99,90</span><p><b>Quero falar sobre o meu negócio:</b> 1 hora de conversa sobre o seu business, PDF com o resumo da reunião e pelo menos uma sacada para alavancar o negócio ou melhorar o posicionamento nas redes.</p><p><b>Gosto do seu conteúdo:</b> 1 hora de conversa sobre o tema que você escolher e 1 vídeo ao final da chamada, sobre esse tema. O assunto fica entre nós.</p><small>Nos dois formatos, voucher de R$ 40,00 para usar no site.</small><a class="btn" href="{AGENDA_ONLINE}">Reservar</a></div></div>
<h2 style="margin-top:28px">Encontre com a especialista</h2>
<div class="grid" style="margin-top:18px"><div class="card"><small>Presencial · São Paulo, SP · 2 horas</small><h3>Reunião presencial</h3><span class="v">R$ 299,90</span><p><b>Quero falar do meu negócio:</b> 2 horas de conversa sobre o seu business, PDF com o resumo e pelo menos duas sacadas para alavancar o negócio ou melhorar o posicionamento nas redes.</p><p><b>Gosto do seu conteúdo:</b> 2 horas de conversa sobre o tema que você escolher e 1 vídeo gravado com você. O assunto fica entre nós.</p><small>Nos dois formatos, voucher de R$ 100,00 para usar no site.</small><a class="btn" href="{AGENDA_PRESENCIAL}">Reservar</a></div></div></div></section></main>'''

# ---------- Privacidade (texto vem do rascunho da pasta concreto-v2) ----------
_priv=open(os.path.join(HERE,'privacidade.body.html'),encoding='utf-8').read()
PRIV=re.search(r'<main>.*?</main>',_priv,re.S).group(0)

DESC='Marketing 360 individual, personalizado e acessível. Método Experimental 30: trinta dias dentro da sua empresa, com relatório no fim. Sem contratos de um ano, sem multas abusivas.'
PAGES=[  # (arquivo, título, descrição, corpo, scripts extras)
 ('index.html','Seu Marketing 360 — por Juliana Aragão',DESC,HOME,JS_LENS),
 ('quem-eu-sou.html','Quem eu sou — Seu Marketing 360','Juliana Aragão S.: mais de 11 anos de redes sociais e marketing, com visão de marketing 360 para micro, pequenas e médias empresas.',BIO,''),
 ('marcas-e-creators.html','Marcas &amp; Creators — Seu Marketing 360','Marcas, creators e projetos da trajetória de Juliana Aragão, com o case New Look Time.',MARCAS,''),
 ('produtos.html','Produtos — Seu Marketing 360','Método Experimental 30, Métodos Trimestral, Semestral e Anual, adicionais e reuniões com a especialista.',PRODUTOS,''),
 ('privacidade.html','Política de privacidade — Seu Marketing 360','Como o site seumarketing360.com.br trata os seus dados, conforme a LGPD.',PRIV,''),
]
def body(cur,main,extra_js): return SCENE+FX+header(cur)+main+FOOTER+JS_COMMON+extra_js
def full(path,title,desc,cur,main,extra_js,with_widget=True):
    robots='<meta name="robots" content="noindex, nofollow">\n' if NOINDEX else ''
    url=BASE+'/'+('' if path=='index.html' else path[:-5])
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Seu Marketing 360">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}/img/icon-512.png">
<meta name="theme-color" content="#B9BCBD">
<link rel="icon" href="img/favicon-64.png" type="image/png"><link rel="apple-touch-icon" href="img/apple-touch-icon.png">
{FONTS}
<style>{CSS}</style>
</head>
<body>
{body(cur,main,extra_js)}
{widget() if with_widget else ''}</body>
</html>
'''
def artifact_index(title,main,extra_js):
    return f'<title>{title}</title>\n{FONTS}\n<style>{CSS}</style>\n{body("index.html",main,extra_js)}\n'
OUT=os.path.join(HERE,'out'); shutil.rmtree(OUT,ignore_errors=True)
for sub in ('dist','artifact'):
    d=os.path.join(OUT,sub); os.makedirs(d); shutil.copytree(os.path.join(HERE,'img'),os.path.join(d,'img'))
    if sub=='dist' and all(ALPHA_TESTER.values()): shutil.copytree(os.path.join(HERE,'js'),os.path.join(d,'js'))
    for path,title,desc,main,js in PAGES:
        cur=path if path!='privacidade.html' else ''
        if sub=='artifact' and path=='index.html': txt=artifact_index('Seu Marketing 360 — site v1',main,js)
        else: txt=full(path,title,desc,cur,main,js,with_widget=(sub=='dist'))
        if sub=='dist':   # Pages serve URLs limpas: /produtos em vez de /produtos.html (evita um redirect por clique)
            txt=re.sub(r'href="index\.html(#[^"]*)?"', lambda m: 'href="/'+(m.group(1) or '')+'"', txt)
            txt=re.sub(r'href="(quem-eu-sou|marcas-e-creators|produtos|privacidade)\.html', r'href="/\1', txt)
        open(os.path.join(d,path),'w',encoding='utf-8').write(txt)
dist=os.path.join(OUT,'dist'); today=datetime.date.today().isoformat()
open(os.path.join(dist,'robots.txt'),'w').write('User-agent: *\nDisallow: /\n' if NOINDEX else f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
open(os.path.join(dist,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}/{"" if p=="index.html" else p[:-5]}</loc><lastmod>{today}</lastmod></url>\n' for p,*_ in PAGES)+'</urlset>\n')
open(os.path.join(dist,'_headers'),'w').write('/img/*\n  Cache-Control: public, max-age=31536000, immutable\n')
host=BASE.split('//')[-1]
open(os.path.join(dist,'_redirects'),'w').write(f'https://www.{host}/* {BASE}/:splat 301\n')
total=sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(dist) for f in fs)
print('out/dist:',sorted(os.listdir(dist)),f'| {total/1024:.0f} KB')
print('out/artifact:',sorted(os.listdir(os.path.join(OUT,'artifact'))))
