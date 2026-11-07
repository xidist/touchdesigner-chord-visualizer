import math, colorsys
import numpy as np
NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
MAJOR = dict(zip('asdfghjkl', [60,62,64,65,67,69,71,72,74]))
PIANO = dict(zip('awsedrftgyjuikol', range(60,76)))
PATTERNS = [('',{0,4,7}),('m',{0,3,7}),('dim',{0,3,6}),('aug',{0,4,8}),('sus2',{0,2,7}),('sus4',{0,5,7}),('7',{0,4,7,10}),('maj7',{0,4,7,11}),('m7',{0,3,7,10})]

def notes(c):
    mapping = MAJOR if c.par.Layout.eval() == 'major' else PIANO
    return sorted({mapping[k] for k in c.fetch('held', set()) if k in mapping})

def blend(ns):
    if not ns: return (0.58,0.3,0.12)
    # Circular hue average: red at 0 and red at 1 are neighbors.
    hs = [(n%12)/12 for n in sorted(set(ns))]
    x=sum(math.cos(h*math.tau) for h in hs); y=sum(math.sin(h*math.tau) for h in hs)
    h=(math.atan2(y,x)/math.tau)%1 if math.hypot(x,y)>1e-6 else hs[0]
    return h,0.8,1.0

def title(ns):
    pcs={n%12 for n in ns}
    for root in sorted(pcs):
        for suffix, intervals in PATTERNS:
            if {(root+i)%12 for i in intervals} == pcs:
                bass=min(ns)%12
                return NAMES[root]+suffix+('/'+NAMES[bass] if bass!=root else '')
    return ' + '.join(NAMES[n%12]+str(n//12-1) for n in ns) or 'PLAY A NOTE'

def key(c, info):
    k=info.key.lower()
    held=set(c.fetch('held',set()))
    if not info.state:
        held.discard(k)
    elif k in ('1','2','space','esc','escape'):
        held.clear()
        if k in ('1','2'): c.par.Layout = 'major' if k=='1' else 'piano'
    elif not (info.ctrl or info.cmd or info.alt):
        held.add(k)
    c.store('held',held)

def audio(out):
    c=out.parent(); out.clear(); out.rate=48000
    count=out.numSamples if out.isTimeSlice and out.numSamples else 800
    out.numSamples=count
    ns=notes(c) if c.par.Enabled else []
    # Independent attack/release envelopes per voice preserve tails, suppress clicks.
    voices=c.fetch('voices',{})
    for n in ns: voices.setdefault(n,[0.0,0.0])
    signal=np.zeros(count,dtype=np.float64)
    for n,(phase,level) in list(voices.items()):
        target=1.0 if n in ns else 0.0
        tau=0.008 if target else 0.09
        env=target+(level-target)*np.exp(-np.arange(1,count+1)/(48000*tau))
        freq=440*2**((n-69)/12)
        angles=phase+np.arange(count)*math.tau*freq/48000
        signal += (np.sin(angles)+0.12*np.sin(2*angles))*env
        voices[n]=[(phase+count*math.tau*freq/48000)%math.tau,float(env[-1])]
        if not target and env[-1]<0.0001: del voices[n]
    c.store('voices',voices)
    signal=np.tanh(signal*0.12)*float(c.par.Volume)
    for name in ('left','right'): out.appendChan(name).vals=signal.tolist()

def draw(out):
    c=out.parent(); ns=notes(c); t=absTime.seconds
    h,s,v=blend(ns); rgb=np.array(colorsys.hsv_to_rgb(h,s,v),dtype=np.float32)
    w,hpx=960,540
    y,x=np.mgrid[0:hpx,0:w].astype(np.float32); x=(x-w/2)/hpx; y=(y-hpx*.57)/hpx
    r=np.sqrt(x*x+y*y)
    energy=1 if ns else .16
    ring=np.maximum(0,np.cos(r*48-t*3))**12*np.exp(-r*4)
    glow=np.exp(-r*6)+.38*ring
    img=np.zeros((hpx,w,4),np.float32); img[:,:,:3]=np.array([.012,.018,.035])+glow[:,:,None]*rgb*energy
    # Each active note keeps its own colored satellite around the blended center.
    for i,n in enumerate(ns):
        angle=(n%12)/12*math.tau-math.pi/2
        rr=np.sqrt((x-.27*math.cos(angle))**2+(y-.27*math.sin(angle))**2)
        col=np.array(colorsys.hsv_to_rgb((n%12)/12,.85,1))
        img[:,:,:3]+=np.exp(-rr[:,:,None]*65)*col*.8
    # Bottom swatches always show the 12-note color map; bright outlines mean held.
    for pc in range(12):
        xx=int(pc*w/12); end=int((pc+1)*w/12)-3
        col=np.array(colorsys.hsv_to_rgb(pc/12,.85,1))
        img[12:40,xx+3:end,:3]=col*(1 if pc in {n%12 for n in ns} else .32)
    img[:,:,:3]=np.clip(img[:,:,:3],0,1); img[:,:,3]=1
    out.copyNumpyArray(img)
    mode='C MAJOR  /  ASDFGHJKL' if c.par.Layout.eval()=='major' else 'PIANO  /  AWSEDRFTGYJUIKOL'
    text = 'CHORD RADIANCE\n'+mode+'\n\n'+title(ns)+'\n'+'  '.join(NAMES[n%12]+str(n//12-1) for n in ns)+'\n\n1  C major     2  Piano     SPACE  all notes off'

    if c.op('label').par.text.eval() != text: c.op('label').par.text=text
