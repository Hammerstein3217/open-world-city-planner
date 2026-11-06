#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the local deliverable, frontmatter and inline source consistency."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/open-world-city-planner'
checks=[]
def check(ok,name):
    checks.append({'name':name,'passed':bool(ok)})
    if not ok:
        raise AssertionError(name)

class HtmlInventory(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.scripts={};self.current=None;self.external=[];self.anchors=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='script':
            if 'src' in a:self.external.append(a['src'])
            self.current=a.get('id')
            if self.current:self.scripts[self.current]=''
        if tag in ['img','iframe','link','audio','video'] and (a.get('src') or a.get('href')):self.external.append(a.get('src') or a.get('href'))
        if tag=='a' and a.get('href','').startswith('#'):self.anchors.append(a['href'][1:])
    def handle_endtag(self,tag):
        if tag=='script':self.current=None
    def handle_data(self,data):
        if self.current:self.scripts[self.current]+=data

content=(SKILL/'SKILL.md').read_text(encoding='utf-8')
m=re.match(r'^---\n(.*?)\n---\n',content,re.S)
check(m is not None,'SKILL.md has bounded frontmatter')
# Deliberately supports this package's simple scalar frontmatter, not arbitrary YAML.
front={}
for line in m.group(1).splitlines():
    k,sep,v=line.partition(':')
    check(bool(sep) and k in ['name','description'],'frontmatter contains supported scalar key '+k)
    front[k]=v.strip()
check(front.get('name')==SKILL.name and bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',front['name'])) and len(front['name'])<=64,'skill naming is valid and matches directory')
check(0<len(front.get('description',''))<=1024 and '<' not in front['description'] and '>' not in front['description'],'description is nonempty and bounded')
check('[TODO:' not in content,'skill entrypoint has no unfinished scaffolding')
paths=set(re.findall(r'`((?:references|assets|scripts)/[^`]+)`',content))
for relative in sorted(paths):check((SKILL/relative).is_file(),'skill resource exists: '+relative)
ui={}
for line in (SKILL/'agents/openai.yaml').read_text(encoding='utf-8').splitlines():
    if line.startswith('  '):
        k,_,v=line.strip().partition(':');ui[k]=json.loads(v.strip())
check(25<=len(ui['short_description'])<=64,'UI short description length fits metadata contract')
check('$open-world-city-planner' in ui['default_prompt'],'default prompt explicitly invokes skill')
html=(ROOT/'demo/index.html').read_text(encoding='utf-8')
inv=HtmlInventory();inv.feed(html)
check(len(inv.ids)==len(set(inv.ids)),'static HTML IDs are unique')
check(not inv.external,'standalone document has no external resource dependencies')
check(all(x in inv.ids for x in inv.anchors),'document outline anchors resolve')
check(json.loads(inv.scripts['city-data'])==json.loads((ROOT/'demo/city.json').read_text(encoding='utf-8')),'embedded city equals source JSON')
check(json.loads(inv.scripts['world-text'])==(ROOT/'demo/worldbuilding.md').read_text(encoding='utf-8'),'embedded worldbuilding equals original source')
check(json.loads(inv.scripts['attachment-text'])==(SKILL/'references/gdc-user-summary.md').read_text(encoding='utf-8'),'embedded GDC method index equals public source')
check(all(token not in html for token in ['__CITY_DATA__','__ATTACHMENT_TEXT__','__WORLD_TEXT__']),'built document has no remaining build tokens')
check('@media(max-width:650px)' in html and '@media print' in html and 'prefers-reduced-motion' in html,'responsive, print and reduced-motion rules are present (not rendered)')
report={'passed':all(x['passed'] for x in checks),'method':'Python standard-library structural checks and restricted scalar frontmatter inspection','checks':checks,'count':len(checks),'officialQuickValidate':'Not completed: bundled quick_validate.py imports PyYAML, which is unavailable. No substitute yaml module or dependency installation was used.','limitations':['Not a general YAML parser or full JSON Schema engine.','CSS presence does not prove layout, browser compatibility or accessibility.','Visual rendering, true keyboard interaction and real browser file opening were not verified.']}
(ROOT/'validation/skill-structure-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'count':report['count']},ensure_ascii=False))
