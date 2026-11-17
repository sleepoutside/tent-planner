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

def funcs(names): return '\n'.join(block('function ' + n + '(') for n in names)

BASE = ['rnd', 'tex', 'label', 'dispose', 'profile', 'loft', 'sections', 'shade', 'surf', 'tOf', 'gridMesh',
        'patch', 'quad', 'tube', 'limb', 'P', 'std', 'rectPts', 'ellPts', 'buildTent1']
NOTE = '/* ---------- builders shared with the simulator (copied from index.html by tools/build.py) ---------- */\n'

# types.html = head template + builders + tail script
wr('types.html', rd(TPL, 'types_head.html') + '\n' + NOTE + funcs(BASE + ['buildPerson', 'car', 'buildTarp1']) + '\n'
   + block('var CARS=') + ';\n' + rd(TPL, 'types_tail.js'))

# fire.html
t = rd(TPL, 'fire.html'); assert t.count('/*BUILDERS*/') == 1
wr('fire.html', t.replace('/*BUILDERS*/', NOTE + funcs(BASE + ['buildPerson'])))

# sleep.html (also needs the TENTS data and sleepArea)
t = rd(TPL, 'sleep.html'); assert t.count('/*BUILDERS*/') == 1 and t.count('/*DATA*/') == 1
i = js.index('var TENTS=['); j = js.index('\n];', i) + 3
wr('sleep.html', t.replace('/*DATA*/', '/* tent data copied from index.html */\n' + js[i:j])
                  .replace('/*BUILDERS*/', NOTE + funcs(BASE + ['sleepArea'])))
print('generated types.html, fire.html, sleep.html')
