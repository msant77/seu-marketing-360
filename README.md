# seumarketing360.com.br

Site da Seu Marketing 360 (Juliana Aragão S.). Site estático em quatro páginas, gerado por um script Python a partir dos textos dela, publicado no Cloudflare Pages.

## Como funciona
- `build.py` gera o site: `python3 build.py` cria `out/dist/` (para hospedar) e `out/artifact/` (para revisão). Textos, links e constantes (WhatsApp, Hotmart, agenda) estão no topo do script.
- `style.css` é o design "Concreto bruto" da Juliana, com os ajustes de v2 (fundo em alta resolução, vidro, menu no celular).
- `img/` tem a foto de fundo (Pexels, Juan Diego, licença livre), os três renders 3D e os ícones.
- `privacidade.body.html` é o rascunho da política de privacidade (LGPD).

## Publicar
Sem CI, como no chordo-pro: depois de cada mudança na `main`, rodar `./deploy.sh` (gera `out/dist` e publica no Cloudflare Pages com o login do wrangler desta máquina). Produção: https://seumarketing360.com.br. Prévia para revisão com o widget: https://seumarketing360.pages.dev.

## Repositório
https://github.com/msant77/seu-marketing-360 (público). Não guardar segredos aqui: a chave do widget é publicável (`at_pub_`), o número do WhatsApp e os links já são públicos no site.

## Ajustes
Cada pedido de ajuste vira uma issue aqui (pelo widget do alpha-tester embutido no site, ou à mão). Rótulos: `conteúdo`, `design`, `bug`, `ajuste`. Todo commit referencia a issue (`… (#12)`); a issue só fecha depois que a Juliana confirma no site publicado.
