/* Offline execution tests in a minimal DOM model, NOT browser/layout tests. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'demo/index.html'),'utf8');
const checks=[],downloads=[],urls=new Map();let printed=0;
function assert(ok,label){if(!ok)throw Error(label);checks.push({name:label,passed:true});}
function attrs(text){const a={};for(const m of text.matchAll(/([:\w-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)){a[m[1]]=m[2]??m[3]??m[4]??'';}return a;}
function decode(s){return s.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,'&');}
class Element{
 constructor(tag,at={},parent=null){this.tagName=tag;this.attrs=at;this.parentElement=parent;this.children=[];this.events={};this._text='';this._html='';this.style={};this.scrollTop=0;this.open=false;this._value=undefined;this._checked=undefined;this.disabled=Object.hasOwn(at,'disabled');const self=this;this.classList={toggle(cls,force){const set=new Set((self.attrs.class||'').split(/\s+/).filter(Boolean));const yes=force===undefined?!set.has(cls):Boolean(force);if(yes)set.add(cls);else set.delete(cls);self.attrs.class=[...set].join(' ');return yes;}};}
 get id(){return this.attrs.id||'';}
 get dataset(){const data={};for(const[k,v]of Object.entries(this.attrs))if(k.startsWith('data-'))data[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;return data;}
 get value(){if(this._value!==undefined)return this._value;if(this.tagName==='select'){const options=this.querySelectorAll('option');return (options.find(x=>Object.hasOwn(x.attrs,'selected'))||options[0])?.attrs.value||'';}return this.attrs.value||'';}
 set value(v){this._value=String(v);}
 get checked(){return this._checked??Object.hasOwn(this.attrs,'checked');}set checked(v){this._checked=Boolean(v);}
 get innerHTML(){return this._html;}set innerHTML(s){this._html=String(s);this._text='';this.children=[];this._value=undefined;parse(this._html,this);}
 get textContent(){return this._text+this.children.map(x=>x.textContent).join('');}set textContent(s){this._text=String(s);this._html=String(s);this.children=[];}
 getAttribute(n){return this.attrs[n]??null;}setAttribute(n,v){this.attrs[n]=String(v);}
 addEventListener(n,fn){(this.events[n]??=[]).push(fn);}
 dispatch(n){for(const f of this.events[n]||[])f({target:this,key:'',preventDefault(){}});}
 querySelectorAll(sel){const all=[];function walk(e){for(const c of e.children){all.push(c);walk(c);}}walk(this);return all.filter(e=>matches(e,sel));}
 querySelector(sel){return this.querySelectorAll(sel)[0]||null;}
 closest(sel){let e=this;while(e){if(matches(e,sel))return e;e=e.parentElement;}return null;}
 scrollIntoView(){}setPointerCapture(){}getBoundingClientRect(){return {width:800,height:600};}
 showModal(){if(this.open)throw Error('dialog already open');this.open=true;}close(){this.open=false;}
 click(){this.dispatch('click');if(this.tagName==='a'&&this.download)downloads.push({name:this.download,body:urls.get(this.href)?.parts.join('')});for(const f of document.events.click||[])f({target:this});}
}
function basic(e,s){if(s.startsWith('#'))return e.id===s.slice(1);if(s.startsWith('.'))return(e.attrs.class||'').split(/\s+/).includes(s.slice(1));const a=s.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);if(a)return Object.hasOwn(e.attrs,a[1])&&(a[2]===undefined||e.attrs[a[1]]===a[2]);return e.tagName===s.toLowerCase();}
function matches(e,selector){return selector.split(',').some(s=>{const parts=s.trim().split(/\s+/);if(!basic(e,parts.pop()))return false;let parent=e.parentElement;while(parts.length){const part=parts.pop();while(parent&&!basic(parent,part))parent=parent.parentElement;if(!parent)return false;parent=parent.parentElement;}return true;});}
function parse(s,parent){const stack=[parent],voids=new Set(['meta','link','input','br','img','hr','path','rect','circle','line','polyline','polygon','output']);let pos=0;for(const m of s.matchAll(/<\/?([a-zA-Z][\w-]*)([^>]*?)>/g)){const current=stack[stack.length-1];current._text+=decode(s.slice(pos,m.index));pos=m.index+m[0].length;const tag=m[1].toLowerCase();if(m[0].startsWith('</')){const i=stack.map(x=>x.tagName).lastIndexOf(tag);if(i>0)stack.length=i;continue;}const el=new Element(tag,attrs(m[2]),current);current.children.push(el);if(!voids.has(tag)&&!m[0].endsWith('/>'))stack.push(el);}stack[stack.length-1]._text+=decode(s.slice(pos));}
const document=new Element('document');document.getElementById=function(id){return this.querySelector('#'+id);};document.createElement=tag=>new Element(tag);
parse(html.replace(/<style[\s\S]*?<\/style>/g,'').replace(/<script[\s\S]*?<\/script>/g,''),document);
for(const m of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)){const at=attrs(m[1]);if(at.id){const el=new Element('script',at,document);el.textContent=m[2];document.children.push(el);}}
const scripts=[...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!attrs(m[1]).type).map(m=>m[2]);
const sandbox={document,window:{print(){printed++;}},console:{log(){},warn(){},error(){}},setTimeout(fn){fn();},Blob:class{constructor(parts,opts){this.parts=parts;this.opts=opts;}},URL:{createObjectURL(blob){const id='blob:test-'+urls.size;urls.set(id,blob);return id;},revokeObjectURL(id){urls.delete(id);}}};vm.createContext(sandbox);for(const script of scripts)new vm.Script(script,{filename:'document-inline.js'}).runInContext(sandbox,{timeout:5000});
const run=s=>vm.runInContext(s,sandbox),get=id=>document.getElementById(id),click=selector=>{const el=document.querySelector(selector);if(!el)throw Error('Missing selector: '+selector);el.click();},change=(id,value)=>{get(id).value=value;get(id).dispatch('change');};
assert(get('cityTitle').textContent==='潮痕港','document initializes without runtime error');
assert(get('cityMap').querySelectorAll('[data-select]').length===34,'current map contains 6 districts, 16 roads and 12 POI');
assert(get('entityRail').querySelectorAll('button').length===6,'district index initializes');
click('[data-select="districts:D06"]');assert(get('dossier').textContent.includes('织巷生活区'),'district selection updates dossier');
assert(get('lifeDistrict').value==='D06'&&get('lifeCards').textContent.includes('23,000'),'district selection synchronizes life chapter');
click('[data-type="pois"]');assert(get('entityRail').querySelectorAll('button').length===12,'POI index shows all twelve');
click('[data-select="pois:P03"]');assert(get('dossier').textContent.includes('双线闸门')&&get('dossier').textContent.includes('周边发生了什么'),'POI dossier includes causal and spatial detail');
click('[data-select="roads:R02"]');assert(get('dossier').textContent.includes('潮尺坡道'),'road selection updates dossier');
click('[data-era="0"]');assert(run('state.era')===0,'timeline changes current era');
assert(!get('cityMap').innerHTML.includes('data-select="pois:P09"'),'timeline hides POI not yet formed');
assert(get('cityMap').querySelectorAll('[data-select]').length===7,'earliest map contains 2 districts, 2 roads and 3 POI');
assert(get('routeResult').textContent.includes('尚未形成'),'routes respect historical existence');
click('[data-era="1"]');assert(get('cityMap').innerHTML.includes('data-select="roads:R17"'),'historical freight road visible before retirement');
click('[data-era="3"]');assert(!get('cityMap').innerHTML.includes('data-select="roads:R17"'),'historical freight road disappears after retirement');
click('[data-era="4"]');
get('mapSearch').value='不存在的城区';get('mapSearch').dispatch('input');assert(get('entityRail').textContent.includes('没有匹配内容'),'search has readable empty state');
get('mapSearch').value='';get('mapSearch').dispatch('input');
change('routeFrom','P02');change('routeTo','P03');assert(run('state.route.roadIds.includes("R02")'),'route uses direct ramp when open');
const direct=run('state.route.seconds');change('routeClosure','R02');assert(!run('state.route.roadIds.includes("R02")')&&run('state.route.seconds')>direct,'closure recomputes a longer legal detour');
change('routeFrom','P01');change('routeTo','P09');change('routeMode','bike');assert(get('routeResult').textContent.includes('没有连续可骑行路线'),'mode restrictions reject unreachable bike route');
change('routeFrom','P08');change('routeTo','P05');change('routeClosure','');get('portPermit').checked=true;get('portPermit').dispatch('change');assert(run('state.route.roadIds.includes("R08")'),'permit enables staff shortcut');
change('routeFrom','P05');assert(run('state.route.lengthM')===0&&run('state.route.seconds')===0,'same origin and destination yields zero route');
get('streetWidth').value='4';get('streetWidth').dispatch('input');assert(get('netWidth').textContent==='2.8','single-variable width budget updates to 2.8m');
click('[data-validation="gate"]');assert(get('validationPanel').textContent.includes('生产尚未放行')&&get('validationPanel').textContent.includes('待实测'),'production gates remain unapproved');
click('[data-event="E03"]');assert(get('eventDetail').textContent.includes('长潮切开城市')&&get('eventDetail').textContent.includes('没有采用'),'history selection shows full causal chain and alternative');
click('[data-faction="F-P"]');assert(run('state.era')===4&&get('mapMode').value==='faction','faction navigation returns to present snapshot');
click('[data-select="districts:D03"]');click('[data-claim="I01"]');assert(get('claim-I01').open&&get('claim-I01').textContent.includes('资本与防洪'),'claim link exposes premises and reasoning');
click('[data-source="GDC-SUM"]');assert(get('readerDialog').open&&get('dialogBody').textContent.includes('Define'),'public GDC method index opens offline');
get('closeDialog').click();get('readWorld').click();assert(get('dialogBody').textContent.includes('W06'),'original worldbuilding opens offline');get('closeDialog').click();
change('claimFilter','measurement');assert(get('claimList').textContent.includes('没有此类记录'),'measurement ledger does not invent observations');
get('downloadData').click();assert(downloads.length===1&&JSON.parse(downloads[0].body).pois.length===12,'data export produces parseable city JSON');
get('printDoc').click();assert(printed===1,'print control invokes document print');
get('zoomIn').click();assert(Number(get('cityMap').getAttribute('viewBox').split(' ')[2])===880,'zoom changes map viewBox');get('zoomReset').click();assert(get('cityMap').getAttribute('viewBox')==='0 0 1100 800','map reset restores overview');
const report={method:'Node vm + minimal DOM model; no browser or layout engine',passed:checks.every(x=>x.passed),count:checks.length,checks,limitations:['No real-browser file opening, visual rendering, screenshot, pointer/keyboard accessibility, print-layout or narrow-screen verification.','A local file URL was rejected by browser protocol policy; no bypass or alternate browser path was used.','No game or engine prototype was built; all whitebox experiments remain not_run.']};
fs.writeFileSync(path.join(root,'validation/document-runtime-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,checks:report.count,method:report.method},null,2));
