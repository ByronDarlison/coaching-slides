"""Draw the Kick Off KFFM example and its teaching variants.

Writes eight SVGs into libraries/kickoff/assets: kffm-example, kffm-widgets,
kffm-status, kffm-days, kffm-flow (animated, plays once), kffm-ai,
kffm-levers and kffm-forecast (used at Q1). Edit the drawing here, then run:

    python3 source/artwork/kickoff/drawings/kffm_drawings.py

Fonts come from the embedded <style> in hag-ladder.svg.
"""
from pathlib import Path
import re
A=str(Path(__file__).resolve().parents[3]/'libraries'/'kickoff'/'assets')+'/'
style=re.search(r'<style>.*?</style>',open(A+'hag-ladder.svg').read()).group(0)
B='#326ab6';INK='#20282f';MUTE='#5b6670';CARD='#f6f4ef'
ST={'g':('#318549','#cdebd3'),'y':('#c9a227','#fbec9d'),'r':('#b84034','#f5c4bd')}
o=[];WL=[];AR=[];BX=[];DY=[];TC=[];BXG=[]
def t(x,y,s,sz,wt=500,c=INK,a='middle'): o.append(f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{wt}" fill="{c}" text-anchor="{a}">{s}</text>')
W_=250;H_=184
def box(x,y,name,owner,days,s,cn):
    c,f=ST[s];cx=x+W_/2;n0=len(o)
    o.append(f'<rect x="{x}" y="{y}" width="{W_}" height="{H_}" rx="12" fill="{f}" stroke="{c}" stroke-width="3"/>')
    t(cx,y+40,name,30,700,B); t(cx,y+72,owner,23); t(cx,y+102,f'+{days} days',21,600,MUTE); DY.append(o[-1])
    ls=cn.split('|'); ls[0]='('+ls[0]; ls[-1]+=')'
    for i,v in enumerate(ls): t(cx,y+138+i*23,v,19,700,INK)
    BX.extend(o[n0:]); BXG.append(o[n0:])
def arrow(x1,y1,x2,y2,label=None,lx=None,ly=None,a='middle'):
    o.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{B}" stroke-width="3" marker-end="url(#a)"/>'); AR.append(o[-1])
    if label:
        ls=label.split('|'); w=max(len(z) for z in ls)*9.6+22; h=len(ls)*21+14
        x0={'middle':lx-w/2,'end':lx-w+11,'start':lx-11}[a]; WL.append((x0,ly-19,w,h,ls,lx,ly,a))
        for i,s in enumerate(ls): t(lx,ly+i*21,s,17,600,B,a)
def sticky(x,y,w,h,lines):
    # White with a blue border: yellow is the legend's "At risk" (Byron, 16-Nov-2026).
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="white" stroke="{B}" stroke-width="3"/>')
    # centre the block: top of the first line's capitals to the last baseline
    cap=lines[0][1]*0.72; span=(len(lines)-1)*38; b0=y+(h-span-cap)/2+cap
    for i,(s,sz,wt) in enumerate(lines): t(x+w/2,round(b0+i*38,1),s,sz,wt,B if i==1 else INK)
W,H=1440,820
y1=40; cy1=y1+H_/2
G=230; X0=200; X1=X0+W_+G; X2=X1+W_+G
box(X0,y1,'Marketing','Chris',14,'y','Sales qualified|subscription leads')
box(X1,y1,'Sales','Andrew',21,'r','New MRR')
box(X2,y1,'Operations','Jen',7,'r','Time to subscription|activation')
arrow(20,cy1,X0-8,cy1,'Subscription|leads',(20+X0)/2,cy1-42)
arrow(X0+W_,cy1,X1-8,cy1,'Marketing qualified|subscription leads',X0+W_+G/2,cy1-42)
arrow(X1+W_,cy1,X2-8,cy1,'New|subscriptions',X1+W_+G/2,cy1-42)
y2=y1+H_+90
box(X2,y2,'Finance','Allison',30,'g','Average days|to collect')
arrow(X2+W_/2,y1+H_,X2+W_/2,y2-8,'Activated|subscriptions',X2+W_/2-16,y1+H_+38,'end')
cy2=y2+H_/2; CX=X1+W_/2
n2=len(o); o.append(f'<circle cx="{CX}" cy="{cy2}" r="84" fill="#e7f2ea" stroke="#318549" stroke-width="4"/>'); t(CX,cy2-6,'$',36,700,'#318549'); t(CX,cy2+30,'Cash',27,700,'#318549'); CASH=o[n2:]
arrow(X2,cy2,CX+92,cy2,'Collected|payments $$$',(X2+CX+92)/2,cy2-38)
sticky(X0-25,cy2-80,300,160,[('Profit per subscription',21,700),('$300 a year',30,700),('Allison',23,500)])
ys=y2+H_+40
o.append(f'<line x1="20" y1="{ys}" x2="1420" y2="{ys}" stroke="{MUTE}" stroke-width="2" stroke-dasharray="8 8"/>')
t(20,ys+36,'Supporting functions',20,700,MUTE,'start')
for i,(n,k,cn) in enumerate([('Development','y','Releases on time'),('IT','g','System uptime'),('People','r','Days to fill a role')]):
    c,f=ST[k]; x=20+i*230; n0=len(o); o.append(f'<rect x="{x}" y="{ys+56}" width="210" height="96" rx="10" fill="{f}" stroke="{c}" stroke-width="3"/>'); t(x+105,ys+96,n,22,700,B); t(x+105,ys+128,'('+cn+')',18,700,INK); BX.extend(o[n0:])
for i,(k,l) in enumerate([('g','On track'),('y','At risk'),('r','Needs attention')]):
    c,f=ST[k]; yy=ys+46+i*30; o.append(f'<rect x="820" y="{yy}" width="24" height="24" rx="4" fill="{f}" stroke="{c}" stroke-width="2"/>'); t(858,yy+19,l,20,600,INK,'start')
t(832,ys+46+3*30+19,'( )',20,700,INK); t(858,ys+46+3*30+19,'Critical number',20,600,INK,'start')
n1=len(o); sticky(X2+W_-310,ys+44,310,104,[('Time to cash',24,700),('72 days',28,700)]); TC.extend(o[n1:])
H=ys+172
open(A+'kffm-example.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'+''.join(o)+'</svg>')
pre=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="HH" viewBox="0 YY {W} HH" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs>'
def lab(ls,lx,ly,a): return ''.join(f'<text x="{lx}" y="{ly+k*21}" font-size="17" font-weight="600" fill="{B}" text-anchor="{a}">{z}</text>' for k,z in enumerate(ls))
hl=''.join(AR)+''.join(lab(ls,lx,ly,a) for x,y,w,h,ls,lx,ly,a in WL)
dim=f'<rect width="{W}" height="{H}" fill="white" opacity=".8"/>'
cx0,cy0,cw,ch=40,cy2-136,600,272
call=(f'<rect x="{cx0+6}" y="{cy0+8}" width="{cw}" height="{ch}" rx="16" fill="#000" opacity=".12"/>'
 f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="16" fill="white" stroke="{B}" stroke-width="4"/>'
 f'<text x="{cx0+32}" y="{cy0+62}" font-size="36" font-weight="700" fill="{B}">Widgets</text>'
 f'<text x="{cx0+32}" y="{cy0+112}" font-size="27" font-weight="500" fill="{INK}">A countable, non-financial thing</text>'
 f'<text x="{cx0+32}" y="{cy0+148}" font-size="27" font-weight="500" fill="{INK}">one function receives and then</text>'
 f'<text x="{cx0+32}" y="{cy0+184}" font-size="27" font-weight="500" fill="{INK}">hands to the next.</text>'
 f'<text x="{cx0+32}" y="{cy0+226}" font-size="27" font-weight="700" fill="{INK}">Widgets drive cash.</text>')
open(A+'kffm-widgets.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'+''.join(o)+dim+hl+call+'</svg>')

def callout(title,lines,h):
    x0,y0=40,cy2-h/2
    r=(f'<rect x="{x0+6}" y="{y0+8}" width="600" height="{h}" rx="16" fill="#000" opacity=".12"/>'
       f'<rect x="{x0}" y="{y0}" width="600" height="{h}" rx="16" fill="white" stroke="{B}" stroke-width="4"/>'
       f'<text x="{x0+32}" y="{y0+62}" font-size="36" font-weight="700" fill="{B}">{title}</text>')
    for i,(sw,l) in enumerate(lines):
        yy=y0+112+i*44
        if sw: c,f=ST[sw]; r+=f'<rect x="{x0+32}" y="{yy-24}" width="28" height="28" rx="6" fill="{f}" stroke="{c}" stroke-width="2.5"/>'
        r+=f'<text x="{x0+(76 if sw else 32)}" y="{yy}" font-size="27" font-weight="500" fill="{INK}">{l}</text>'
    return r
st=callout('Rated by the critical number',[('g','On track'),('y','At risk'),('r','Needs attention')],250)
open(A+'kffm-status.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'+''.join(o)+dim+''.join(BX)+st+'</svg>')

dc=callout('Days to cash',[(None,'Add the days each function takes:'),(None,'14 + 21 + 7 + 30 = 72 days'),(None,'from subscription lead to cash.')],250)
dyb=''.join(z.replace('fill="#5b6670"','fill="#326ab6"').replace('font-size="21"','font-size="23"').replace('font-weight="600"','font-weight="700"') for z in DY)
open(A+'kffm-days.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'+''.join(o)+dim+''.join(CASH)+dyb+''.join(TC)+dc+'</svg>')

# ---- cash forecast (Q1): the same map, one month of widgets (Byron, 16-Nov-2026) ----
fc=callout('One month of widgets',[(None,'650 subscription leads in January'),(None,'become 65 new subscriptions,'),(None,'worth $16,250 a month,'),(None,'collected about 72 days later, in March.')],280)
open(A+'kffm-forecast.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'+''.join(o)+dim+''.join(z for g in BXG[:4] for z in g if z not in DY)+hl+''.join(CASH)+dyb+''.join(TC)+fc+'</svg>')

# ---- animated flow (slide 15) ----
T=13.0
def kt(t): return f'{t/T:.4f}'
base=[z for z in o if z not in TC]
n_tc=len(TC)
sx,sy=X2+W_-310,ys+44
stk=f'<rect x="{sx}" y="{sy}" width="310" height="104" rx="10" fill="white" stroke="{B}" stroke-width="3"/><text x="{sx+155}" y="{sy+41.6}" font-size="24" font-weight="700" fill="{INK}" text-anchor="middle">Time to cash</text>'
# waypoints (time, distance)
TOT=1935
wp=[(0,0),(0.8,180),(2.6,430),(3.4,660),(5.2,910),(6.0,1140),(7.0,1357),(7.6,1447),(9.6,1664),(10.4,1935),(T,1935)]
kts=';'.join(kt(t) for t,_ in wp); kps=';'.join(f'{d/TOT:.4f}' for _,d in wp)
path=f'M20,{cy1} L{X2+W_/2},{cy1} L{X2+W_/2},{cy2} L{CX+84},{cy2}'
tok=(f'<g><rect x="-15" y="-15" width="30" height="30" rx="7" fill="{B}"/>'
     f'<animateMotion dur="{T}s" repeatCount="indefinite" path="{path}" keyTimes="{kts}" keyPoints="{kps}" calcMode="linear"/>'
     f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="1;0" keyTimes="0;{kt(10.3)}" calcMode="discrete"/></g>')
# dwell highlights
dw=[(X0,y1,0.8,2.6),(X1,y1,3.4,5.2),(X2,y1,6.0,7.0),(X2,y2,7.6,9.6)]
hl2=''.join(f'<rect x="{x-6}" y="{y-6}" width="{W_+12}" height="{H_+12}" rx="16" fill="none" stroke="{B}" stroke-width="6" opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;1;0" keyTimes="0;{kt(a)};{kt(b)}" calcMode="discrete"/></rect>' for x,y,a,b in dw)
# cash pulse
pulse=(f'<circle cx="{CX}" cy="{cy2}" r="84" fill="none" stroke="#318549" stroke-width="6" opacity="0">'
       f'<animate attributeName="r" dur="{T}s" repeatCount="indefinite" values="84;84;118;118" keyTimes="0;{kt(10.4)};{kt(11.6)};1"/>'
       f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;0;1;0;0" keyTimes="0;{kt(10.39)};{kt(10.45)};{kt(11.6)};1"/></circle>'
       f'<circle cx="{CX}" cy="{cy2}" r="84" fill="#318549" opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;0;1;1;1" keyTimes="0;{kt(10.4)};{kt(10.8)};{kt(12.6)};1"/></circle>'
       f'<text x="{CX}" y="{cy2+14}" font-size="44" font-weight="700" fill="white" text-anchor="middle" opacity="0">$$$<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;0;1;1;1" keyTimes="0;{kt(10.4)};{kt(10.8)};{kt(12.6)};1"/></text>')
# day counter
segs=[(0.8,2.6,0,14),(3.4,5.2,14,35),(6.0,7.0,35,42),(7.6,10.4,42,72)]
start={0:0.0}
for a,b,v0,v1 in segs:
    for n in range(v0+1,v1+1): start[n]=a+(b-a)*(n-v0)/(v1-v0)
cnt=''
for n in range(0,73):
    a=start[n]; b=start.get(n+1)
    if n==0: vals,keys='1;0',f'0;{kt(b)}'
    elif b is None: vals,keys='0;1',f'0;{kt(a)}'
    else: vals,keys='0;1;0',f'0;{kt(a)};{kt(b)}'
    cnt+=f'<text x="{sx+155}" y="{sy+79.6}" font-size="30" font-weight="700" fill="{INK}" text-anchor="middle" opacity="0">{n} days<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="{vals}" keyTimes="{keys}" calcMode="discrete"/></text>'
def win(els,a,b):
    v,k=('1;0',f'0;{kt(b)}') if a==0 else ('0;1;0',f'0;{kt(a)};{kt(b)}')
    return f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="{v}" keyTimes="{k}" calcMode="discrete"/>'+''.join(els)+'</g>'
arwin=[(0,0.8),(2.6,3.4),(5.2,6.0),(7.0,7.6),(9.6,10.4)]
bright=''
for k,(a,b) in enumerate(arwin):
    x,y,w,h,ls,lx,ly,an=WL[k]
    bright+=win([AR[k],lab(ls,lx,ly,an)],a,b+0.15)
for k,(x,y,a,b) in enumerate(dw): bright+=win(BXG[k],a,b)
bright+=f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;1;1" keyTimes="0;{kt(10.4)};1" calcMode="discrete"/>'+''.join(CASH)+'</g>'
tok_top=tok
open(A+'kffm-flow.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'+(''.join(base)+dim+tok_top+bright+hl2+pulse+stk+cnt).replace('repeatCount="indefinite"','fill="freeze"')+'</svg>')

# ---- AI roadmap (slide 22) ----
aw,ah=640,390; ax0,ay0=40,ys-16-ah-8  # clear the dashed divider, shadow included
ai=(f'<rect x="{ax0+6}" y="{ay0+8}" width="{aw}" height="{ah}" rx="16" fill="#000" opacity=".12"/>'
    f'<rect x="{ax0}" y="{ay0}" width="{aw}" height="{ah}" rx="16" fill="white" stroke="{B}" stroke-width="4"/>'
    f'<text x="{ax0+32}" y="{ay0+56}" font-size="30" font-weight="700" fill="{B}">Every function already defines</text>'
    f'<text x="{ax0+32}" y="{ay0+94}" font-size="30" font-weight="700" fill="{B}">what AI needs</text>')
for i,(k,v) in enumerate([('Receives','New subscriptions'),('Produces','Activated subscriptions'),('Critical number','Time to activation'),('Days','7')]):
    yy=ay0+146+i*38
    ai+=f'<text x="{ax0+32}" y="{yy}" font-size="25" font-weight="700" fill="{INK}">{k}:</text><text x="{ax0+250}" y="{yy}" font-size="25" font-weight="500" fill="{INK}">{v}</text>'
ai+=(f'<line x1="{ax0+32}" y1="{ay0+300}" x2="{ax0+aw-32}" y2="{ay0+300}" stroke="#e1ded6" stroke-width="2"/>'
     f'<text x="{ax0+32}" y="{ay0+334}" font-size="22" font-weight="600" fill="{INK}">Start with the smallest, lowest-risk piece.</text>'
     f'<text x="{ax0+32}" y="{ay0+362}" font-size="22" font-weight="600" fill="{INK}">The critical number tells you if it worked.</text>')
def lw(k):
    x,y,w,h,ls,lx,ly,an=WL[k]; return AR[k]+lab(ls,lx,ly,an)
open(A+'kffm-ai.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{B}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'+''.join(o)+dim+lw(2)+lw(3)+''.join(BXG[2])+ai+'</svg>')

# ---- six levers (slide 22): the example plus the lever cards ----
ex=open(A+'kffm-example.svg').read()
style=re.search(r'<style>.*?</style>',ex).group(0)
EH=int(re.search(r'viewBox="0 0 1440 (\d+)"',ex).group(1)); MH=round(EH*1460/1440); MY=round((96+896)/2-MH/2)
inner=re.sub(r'^<svg[^>]*>','',ex); inner=inner[:inner.rfind('</svg>')]
inner=inner.replace(style,'').replace('id="a"','id="am"').replace('url(#a)','url(#am)')
B='#326ab6';INK='#20282f';MUTE='#5b6670';G='#318549'
L=[('Quantity','More in','More widgets into the first function.'),('Conversion','More through','More widgets pass each hand-off.'),('Price','More per sale','Raise the price customers pay.'),('Timing','Faster','Fewer days from first widget to cash.'),('Capacity','More per month','Each function handles more widgets a month.'),('Cost','Less out','Lower what each function costs to run.')]
o=[]
x0=1490
for i,(r,h,s) in enumerate(L):
    y=96+i*136
    c=G if i==5 else B
    o.append(f'<rect x="{x0}" y="{y}" width="680" height="124" rx="10" fill="#f6f4ef" stroke="#e1ded6"/><rect x="{x0}" y="{y}" width="8" height="124" rx="4" fill="{c}"/>')
    o.append(f'<text x="{x0+30}" y="{y+29}" font-size="21" font-weight="700" fill="{MUTE}" letter-spacing="1">{r.upper()}</text>')
    o.append(f'<text x="{x0+30}" y="{y+78}" font-size="42" font-weight="700" fill="{INK}">{h}</text>')
    o.append(f'<text x="{x0+30}" y="{y+112}" font-size="29" font-weight="500" fill="{INK}">{s}</text>')
W,H=2200,936
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{style}<rect width="{W}" height="{H}" fill="white"/><g><svg x="0" y="{MY}" width="1460" height="{MH}" viewBox="0 0 1440 {EH}">{inner}</svg></g>'+''.join(o)+'</svg>'
open(A+'kffm-levers.svg','w').write(svg)

# ---- projector type (16-Nov-2026): raise the smallest type in every KFFM drawing ----
# Only font sizes change, so no shape moves and the hotspot boxes stay valid.
TYPE={'17':'21','18':'20','19':'21','20':'22','21':'22'}
for f in sorted(Path(A).glob('kffm-*.svg')):
    s=f.read_text(); cut=s.index('</style>')+8
    f.write_text(s[:cut]+re.sub(r'font-size="([\d.]+)"',lambda g:f'font-size="{TYPE.get(g.group(1),g.group(1))}"',s[cut:]))
