#!/usr/bin/env python3
"""Render the 1200x630 share-preview images (og-index.jpg, og-types.jpg, og-tarps.jpg, og-fire.jpg, og-sleep.jpg, og-weather.jpg).

Needs: playwright (python) + Google Chrome, and a local copy of three.js r128:
    THREE_JS=/path/to/three.min.js python3 tools/make_og.py
Re-run only when the look of a page changes enough that the preview is misleading.
"""
import asyncio, base64, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THREE = os.environ.get('THREE_JS')
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')
ARGS = ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
PAGES = {'index': ('帳篷 × 營位', '3D 搭設模擬', '選帳、選營位，放不放得下一眼就知道'),
         'types': ('帳篷型式', '3D 介紹與優缺點', '11 種帳型加 2 種天幕的優缺點'),
         'tarps': ('天幕搭法', '3D 介紹', '同一張天幕的八種搭法'),
         'fire': ('焚火安全模擬', '', '焚火台、燃料、風向與安全距離'),
         'sleep': ('帳內睡鋪模擬', '', '這頂帳到底睡得下幾個人'),
         'weather': ('營地天氣模擬', '', '拖曳時間軸，用 3D 看週末每小時的雨、風和日夜')}
WIDE = '.stage > *:not(canvas){display:none!important} .stage{height:820px!important}'
BOX = ('.stage > *:not(canvas){display:none!important} .stage{position:fixed!important;left:0;top:0;'
       'width:860px!important;height:630px!important;z-index:999;border-radius:0!important;border:0!important}')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
        import sys
        only = sys.argv[1:]
        for n, (t1, t2, sub) in PAGES.items():
            if only and n not in only: continue
            pg = await b.new_page(viewport={'width': 2200, 'height': 1000}, device_scale_factor=1 if n == 'index' else 2)
            async def three(r):
                if THREE: await r.fulfill(path=THREE, content_type='application/javascript')
                else: await r.continue_()
            await pg.route('**/three.min.js', three)
            await pg.route('**/gc.zgo.at/**', lambda r: r.abort())
            await pg.route('**/abacus.jasoncameron.dev/**', lambda r: r.abort())
            await pg.goto('file://' + os.path.join(ROOT, n + '.html'))
            await pg.add_style_tag(content=WIDE if n == 'index' else BOX)
            await pg.wait_for_timeout(1500)
            if n == 'index': await pg.evaluate("document.querySelector('#labels').click()")
            await pg.wait_for_timeout(600)
            uri = 'data:image/png;base64,' + base64.b64encode(await pg.locator('canvas').first.screenshot()).decode()
            img = 'inset:0;width:100%' if n == 'index' else 'right:0;top:0;width:860px'
            grad = ('rgba(20,38,30,.72) 36%,rgba(20,38,30,0) 68%' if n == 'index'
                    else 'rgba(20,38,30,1) 28%,rgba(20,38,30,.55) 46%,rgba(20,38,30,0) 70%')
            html = f'''<html><body style="margin:0;width:1200px;height:630px;position:relative;overflow:hidden;background:#14261e;font-family:'Noto Sans CJK TC','Noto Sans TC',sans-serif">
<img src="{uri}" style="position:absolute;{img};height:100%;object-fit:cover;object-position:50% 55%">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,38,30,.9) 0%,{grad})"></div>
<div style="position:absolute;left:64px;top:0;bottom:0;width:560px;display:flex;flex-direction:column;justify-content:center;color:#fff">
<div style="font-size:66px;font-weight:900;line-height:1.18;letter-spacing:.01em">{t1}{'<br>' + t2 if t2 else ''}</div>
<div style="width:72px;height:6px;background:#f2b233;border-radius:3px;margin:26px 0 22px"></div>
<div style="font-size:31px;font-weight:500;line-height:1.4;color:#e8efe9">{sub}</div></div>
<div style="position:absolute;left:64px;bottom:40px;color:#cfe0d5;font-size:24px;font-weight:700;letter-spacing:.04em">Sleepoutside Camp</div></body></html>'''
            c = await b.new_page(viewport={'width': 1200, 'height': 630})
            await c.set_content(html); await c.wait_for_timeout(300)
            await c.screenshot(path=os.path.join(ROOT, f'og-{n}.jpg'), type='jpeg', quality=86)
            await c.close(); await pg.close(); print('og-' + n + '.jpg')
        await b.close()
asyncio.run(main())
