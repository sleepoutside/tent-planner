#!/usr/bin/env python3
"""Smoke test: load all four pages at desktop and phone size, fail on JS errors or horizontal overflow.

    THREE_JS=/path/to/three.min.js python3 tools/smoke.py
(THREE_JS is only needed when the machine cannot reach cdnjs.) Needs playwright + Google Chrome.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THREE = os.environ.get('THREE_JS')
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')
ARGS = ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']

async def main():
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
        for name in ['index', 'types', 'tarps', 'fire', 'sleep']:
            for vp in [{'width': 1280, 'height': 800}, {'width': 390, 'height': 780}]:
                pg = await b.new_page(viewport=vp); errs = []
                pg.on('pageerror', lambda e: errs.append(str(e)))
                async def three(r):
                    if THREE: await r.fulfill(path=THREE, content_type='application/javascript')
                    else: await r.continue_()
                await pg.route('**/three.min.js', three)
                await pg.route('**/gc.zgo.at/**', lambda r: r.abort())
                await pg.route('**/abacus.jasoncameron.dev/**', lambda r: r.abort())
                await pg.goto('file://' + os.path.join(ROOT, name + '.html')); await pg.wait_for_timeout(1000)
                over = await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
                webgl = await pg.evaluate("!!document.querySelector('canvas') && document.querySelector('canvas').width>0")
                ok = not errs and over <= 0 and webgl
                bad += 0 if ok else 1
                print(('ok  ' if ok else 'FAIL'), name, vp['width'], 'overflow', over, errs)
                await pg.close()
        await b.close()
    sys.exit(1 if bad else 0)
asyncio.run(main())
