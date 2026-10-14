# seumarketing360.com.br

Site da Seu Marketing 360 (Juliana Aragão S.). Site estático em quatro páginas, gerado por um script Python a partir dos textos dela, publicado no Cloudflare Pages.

## Como funciona
- `build.py` gera o site: `python3 build.py` cria `out/dist/` (para hospedar) e `out/artifact/` (para revisão). Textos, links e constantes (WhatsApp, Hotmart, agenda) estão no topo do script.
- `style.css` é o design "Concreto bruto" da Juliana, com os ajustes de v2 (fundo em alta resolução, vidro, menu no celular).
- `img/` tem a foto de fundo (Pexels, Juan Diego, licença livre), os três renders 3D e os ícones.
- `privacidade.body.html` é o rascunho da política de privacidade (LGPD).

## Publicar
```bash
python3 build.py
wrangler pages deploy out/dist --project-name seumarketing360 --branch main --commit-dirty=true
```
Produção: https://seumarketing360.pages.dev (domínio seumarketing360.com.br quando o DNS apontar).

## Ajustes
Cada pedido de ajuste vira uma issue aqui (manualmente ou pelo widget do alpha-tester embutido no site). Rótulos: `conteúdo`, `design`, `bug`, `ajuste`.
