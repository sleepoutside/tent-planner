#!/usr/bin/env python3
"""Regenerate types.html, fire.html and sleep.html from index.html + tools/tpl/.

The three pages reuse the simulator's 3D builder functions. Those functions live
only in index.html; this script copies them (by brace matching) into each page.
Run after ANY change to the shared builders or TENTS data in index.html:

    python3 tools/build.py
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, 'tools', 'tpl')
def rd(*p): return open(os.path.join(*p), encoding='utf-8').read()
def wr(name, s): open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(s)

js = re.findall(r'<script>(.*?)</script>', rd(ROOT, 'index.html'), re.S)[0]

def block(start):
    """Return the source from `start` to its matching closing brace."""
    i = js.index(start); k = js.index('{', i); d = 0; instr = None
    while True:
        ch = js[k]
        if instr:
            if ch == '\\': k += 1
            elif ch == instr: instr = None
        elif ch in '"\'': instr = ch
        elif ch == '{': d += 1
        elif ch == '}':
            d -= 1
            if d == 0: break
        k += 1
    return js[i:k + 1]

NAVCSS = '''  .navcards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;flex:0 1 590px;min-width:0}
  .navcards a{display:flex;flex-direction:column;justify-content:center;gap:1px;min-height:52px;padding:6px 4px;text-align:center;text-decoration:none;border-radius:10px;border:1px solid #c5dccd;background:var(--accent-soft);color:var(--accent);font-weight:700;font-size:14px;line-height:1.3}
  .navcards a small{font-weight:500;font-size:11px;color:var(--muted)}
  .navcards a:hover{background:var(--accent);border-color:var(--accent);color:#fff}
  .navcards a:hover small{color:#e2eee6}
  @media (max-width: 880px){ .navcards{flex:1 1 100%;margin-top:4px;gap:6px} .navcards a{font-size:13px} .navcards a small{font-size:10px} }'''
CARDS = [('index', '搭設模擬', '放不放得下'), ('types', '帳型介紹', '3D 與優缺點'), ('tarps', '天幕搭法', '八種搭法'),
         ('fire', '焚火安全', '距離與風向'), ('sleep', '帳內睡鋪', '睡得下幾人'), ('weather', '露營天氣online', '週末 3D 天氣')]
def nav(me):
    """Navigation cards to every page except `me`. index.html keeps its own hand-written copy."""
    return ('<nav class="navcards" aria-label="其他頁面">'
            + ''.join(f'<a href="{k}.html">{t}<small>{s}</small></a>' for k, t, s in CARDS if k != me) + '</nav>')
def page(name, html):
    assert html.count('/*NAV*/') == 1 and html.count('/*NAVCSS*/') == 1, name
    wr(name + '.html', html.replace('/*NAVCSS*/', NAVCSS).replace('/*NAV*/', nav(name)))

def funcs(names): return '\n'.join(block('function ' + n + '(') for n in names)

BASE = ['rnd', 'tex', 'label', 'dispose', 'profile', 'loft', 'sections', 'shade', 'surf', 'tOf', 'gridMesh',
        'patch', 'quad', 'tube', 'limb', 'P', 'std', 'rectPts', 'ellPts', 'buildTent1']
NOTE = '/* ---------- builders shared with the simulator (copied from index.html by tools/build.py) ---------- */\n'

# types.html = head template + builders + tail script
page('types', rd(TPL, 'types_head.html') + '\n' + NOTE + funcs(BASE + ['buildPerson', 'car', 'buildTarp1']) + '\n'
   + block('var CARS=') + ';\n' + rd(TPL, 'types_tail.js'))

# fire.html
t = rd(TPL, 'fire.html'); assert t.count('/*BUILDERS*/') == 1
page('fire', t.replace('/*BUILDERS*/', NOTE + funcs(BASE + ['buildPerson'])))

# sleep.html (also needs the TENTS data and sleepArea)
t = rd(TPL, 'sleep.html'); assert t.count('/*BUILDERS*/') == 1 and t.count('/*DATA*/') == 1
i = js.index('var TENTS=['); j = js.index('\n];', i) + 3
page('sleep', t.replace('/*DATA*/', '/* tent data copied from index.html */\n' + js[i:j])
                  .replace('/*BUILDERS*/', NOTE + funcs(BASE + ['sleepArea'])))

# tarps.html
t = rd(TPL, 'tarps.html'); assert t.count('/*BUILDERS*/') == 1
page('tarps', t.replace('/*BUILDERS*/', NOTE + funcs(BASE + ['buildPerson', 'car']) + '\n' + block('var CARS=') + ';'))
# weather.html
t = rd(TPL, 'weather.html'); assert t.count('/*BUILDERS*/') == 1
def arr(start):
    i = js.index(start); j = js.index('\n];', i) + 3
    return js[i:j]
def line(start):
    i = js.index(start); j = js.index('\n', i)
    return js[i:j]
page('weather', t.replace('/*BUILDERS*/', NOTE + funcs(BASE + ['buildPerson', 'car', 'buildTarp1', 'buildProp', 'placeProp', 'swapS',
                                                              'b64u', 'unb64u', 'r2', 'nn', 'cl']) + '\n' + block('var CARS=') + ';\n'
     + '/* data copied from index.html */\n' + arr('var TENTS=[') + '\n' + arr('var TARPS=[') + '\n' + line('var CHAIR_SIZE=') + '\n'
     + line('var TABLE_SIZE=') + '\n' + block('var PROPS=') + ';\nvar FIRE_IN=3,FIRE_OUT=4.5;\n' + block('var CUSTOM2=') + ';'))
print('generated types.html, fire.html, sleep.html, tarps.html, weather.html')
