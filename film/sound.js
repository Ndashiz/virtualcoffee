/* ---------------- THE ROOM'S SOUND (the trailer's score) ----------------
   The café had a voice and a jukebox and nothing else: a room with eleven
   people and an espresso machine in dead silence is the loudest "this is a
   render" there is. Everything here is SYNTHESISED — no file to load, no
   licence to track: a room tone and the street through the glass; a walla
   of distant conversation (five voices: a glottal saw through two formant
   filters, vowels and syllables at speaking rate, a breath of consonant
   noise on each onset, all of it low-passed like talk across a room); and
   the bar's own sounds cued by what the barista is doing — the grinder
   while she grinds, the knock of the portafilter, the pump through the
   pull, the steam wand, the clink of the cup she serves — plus the door's
   bell, a car now and then, a cup set down at a table. Each event is placed
   (gain by distance, pan by bearing from the lens). It ducks under Simon's
   voice and under the jukebox, obeys the page's mute, and goes quiet at
   closing time. The builder takes any context, so the same code renders
   offline (OfflineAudioContext) for listening tests.
   It ran live on the page for one day (DA audit, phase 4) and was taken
   off it on 2026-09-30 — Simon: "je ne veux plus de bruit de fond". It
   lives on here, and only here, to score the trailer. */
function ambBuild(ctx,dest){
  const S={ctx:ctx,crowdOn:true};
  const master=ctx.createGain();master.gain.value=1;master.connect(dest);
  const duck=ctx.createGain();duck.gain.value=1;duck.connect(master);
  const out=ctx.createGain();out.gain.value=0;out.connect(duck);
  out.gain.setTargetAtTime(1,ctx.currentTime+.2,1.2);          /* fade in */
  S.master=master;S.duck=duck;S.out=out;
  function noiseBuf(sec,brown){
    const n=ctx.sampleRate*sec|0,b=ctx.createBuffer(1,n,ctx.sampleRate),d=b.getChannelData(0);
    let l=0;for(let i=0;i<n;i++){const w=Math.random()*2-1;if(brown){l=(l+.02*w)/1.02;d[i]=l*3.5;}else d[i]=w;}
    return b;
  }
  const WHITE=noiseBuf(3,false),BROWN=noiseBuf(5,true);
  function src(buf,t,loop){const s=ctx.createBufferSource();s.buffer=buf;s.loop=!!loop;
    s.loopEnd=buf.duration;s.start(t||0,Math.random()*buf.duration*.9);return s;}
  function filt(type,f,q){const b=ctx.createBiquadFilter();b.type=type;b.frequency.value=f;if(q)b.Q.value=q;return b;}
  function place(v){                     /* {g,p} -> a gain+pan into out */
    const g=ctx.createGain();g.gain.value=v&&v.g!==undefined?v.g:1;
    if(ctx.createStereoPanner){const pn=ctx.createStereoPanner();pn.pan.value=v&&v.p||0;g.connect(pn);pn.connect(out);}
    else g.connect(out);
    return g;
  }
  function env(param,t,a,peak,hold,rel){
    param.setValueAtTime(0,t);param.linearRampToValueAtTime(peak,t+a);
    param.setValueAtTime(peak,t+a+hold);param.setTargetAtTime(0,t+a+hold,rel/4);
  }
  /* --- beds --- */
  {const s=src(BROWN,0,true),f=filt("lowpass",280),g=ctx.createGain();g.gain.value=.05;s.connect(f);f.connect(g);g.connect(out);}
  {const s=src(BROWN,0,true),f=filt("lowpass",170),g=ctx.createGain();g.gain.value=.07;s.connect(f);f.connect(g);g.connect(out);S.street=g;}
  /* the fridge's compressor: a 50 Hz hum and its octave, barely there */
  {const o=ctx.createOscillator(),o2=ctx.createOscillator(),g=ctx.createGain();o.frequency.value=50;o2.frequency.value=100;
   g.gain.value=.006;o.connect(g);o2.connect(g);g.connect(place({g:1,p:.3}));o.start();o2.start();}
  /* --- the walla: five voices --- */
  const VOW=[[800,1200],[500,1800],[320,2300],[520,920],[340,800],[520,1500],[660,1700]];
  S.voices=[];
  for(let i=0;i<5;i++){
    const fem=i%2===1,o=ctx.createOscillator();o.type="sawtooth";
    const f0=fem?185+Math.random()*50:98+Math.random()*30;o.frequency.value=f0;
    const f1=filt("bandpass",500,6),f2=filt("bandpass",1500,9),mix=ctx.createGain(),lp=filt("lowpass",1300),g=ctx.createGain();
    g.gain.value=0;o.connect(f1);o.connect(f2);f1.connect(mix);f2.connect(mix);mix.gain.value=.6;
    mix.connect(lp);lp.connect(g);
    const nz=src(WHITE,0,true),nf=filt("bandpass",4200,1.2),ng=ctx.createGain();ng.gain.value=0;
    nz.connect(nf);nf.connect(ng);ng.connect(lp);
    g.connect(place({g:.55,p:(i/4-.5)*1.2}));o.start();
    S.voices.push({o:o,f1:f1,f2:f2,g:g,ng:ng,f0:f0,next:Math.random()*2,lvl:.018+Math.random()*.012});
  }
  /* syllables up to t1 (called ahead of time, realtime or offline) */
  S.murmur=function(t0,t1){
    if(!S.crowdOn)return;
    S.voices.forEach(function(v){
      let t=Math.max(v.next,t0);
      while(t<t1){
        const n=2+Math.random()*9|0;                      /* a phrase */
        for(let k=0;k<n&&t<t1+2;k++){
          const w=VOW[Math.random()*VOW.length|0],d=.11+Math.random()*.13;
          v.f1.frequency.setTargetAtTime(w[0]*(v.f0>150?1.12:1),t,.025);
          v.f2.frequency.setTargetAtTime(w[1]*(v.f0>150?1.1:1),t,.025);
          v.o.frequency.setTargetAtTime(v.f0*(1+(Math.random()-.5)*.25)*(1-k*.012),t,.04);
          env(v.g.gain,t,.03,v.lvl*(.7+Math.random()*.6),d*.5,d);
          if(Math.random()<.6)env(v.ng.gain,t-.01,.005,.04,.02,.04);
          t+=d+.03+Math.random()*.06;
        }
        t+=.4+Math.random()*2.2;                          /* breath, listening */
      }
      v.next=t;
    });
  };
  /* --- the bar --- */
  S.grind=function(t,dur,v){
    const g=place(v),e=ctx.createGain();e.connect(g);env(e.gain,t,.08,.5,dur-.4,.35);
    const o=ctx.createOscillator();o.type="sawtooth";o.frequency.setValueAtTime(90,t);
    o.frequency.linearRampToValueAtTime(155,t+.15);const lp=filt("lowpass",700);o.connect(lp);
    const og=ctx.createGain();og.gain.value=.35;lp.connect(og);og.connect(e);o.start(t);o.stop(t+dur+.5);
    const n=src(WHITE,t,true),bp=filt("bandpass",2600,.9),ng=ctx.createGain();ng.gain.value=.55;
    const lfo=src(WHITE,t,true),lf=filt("lowpass",38),lg=ctx.createGain();lg.gain.value=.9;
    lfo.connect(lf);lf.connect(lg);lg.connect(ng.gain);
    n.connect(bp);bp.connect(ng);ng.connect(e);n.stop(t+dur+.5);lfo.stop(t+dur+.5);
  };
  S.knock=function(t,v){
    const g=place(v),o=ctx.createOscillator(),e=ctx.createGain();
    o.frequency.setValueAtTime(140,t);o.frequency.exponentialRampToValueAtTime(48,t+.09);
    e.gain.setValueAtTime(.9,t);e.gain.setTargetAtTime(0,t+.01,.05);o.connect(e);e.connect(g);o.start(t);o.stop(t+.4);
    const n=src(WHITE,t,true),hp=filt("highpass",2500),ne=ctx.createGain();
    ne.gain.setValueAtTime(.25,t);ne.gain.setTargetAtTime(0,t,.008);n.connect(hp);hp.connect(ne);ne.connect(g);n.stop(t+.1);
  };
  S.pump=function(t,dur,v){
    const g=place(v),e=ctx.createGain();e.connect(g);env(e.gain,t,.3,1,dur-.8,.5);
    const o=ctx.createOscillator();o.type="square";o.frequency.value=49;
    const lp=filt("lowpass",220),og=ctx.createGain();og.gain.value=.05;o.connect(lp);lp.connect(og);og.connect(e);o.start(t);o.stop(t+dur+.6);
    const n=src(WHITE,t+2,true),bp=filt("bandpass",3300,2.2),ng=ctx.createGain();ng.gain.value=0;
    ng.gain.setValueAtTime(0,t+2);ng.gain.linearRampToValueAtTime(.011,t+3);
    n.connect(bp);bp.connect(ng);ng.connect(e);n.stop(t+dur+.6);
  };
  S.steam=function(t,dur,v){
    const g=place(v),e=ctx.createGain();e.connect(g);env(e.gain,t,.15,.13,dur-.6,.4);
    const n=src(WHITE,t,true),hp=filt("highpass",2200),pk=filt("peaking",3600,3);pk.gain.value=8;
    pk.frequency.setValueAtTime(3200,t);pk.frequency.linearRampToValueAtTime(5200,t+dur*.8);
    const am=ctx.createGain();am.gain.value=.7;const lfo=ctx.createOscillator();lfo.frequency.value=17;
    const lg=ctx.createGain();lg.gain.value=.3;lfo.connect(lg);lg.connect(am.gain);
    n.connect(hp);hp.connect(pk);pk.connect(am);am.connect(e);lfo.start(t);lfo.stop(t+dur+.6);n.stop(t+dur+.6);
  };
  S.clink=function(t,v,k){
    const g=place(v);k=k||(.9+Math.random()*.2);
    [[2350,1,.35],[3810,.6,.22],[5230,.4,.15],[6900,.2,.08]].forEach(function(m){
      const o=ctx.createOscillator(),e=ctx.createGain();o.frequency.value=m[0]*k;
      e.gain.setValueAtTime(m[1]*.09,t);e.gain.setTargetAtTime(0,t,m[2]/3);o.connect(e);e.connect(g);o.start(t);o.stop(t+m[2]*2);
    });
    const n=src(WHITE,t,true),hp=filt("highpass",4000),ne=ctx.createGain();
    ne.gain.setValueAtTime(.05,t);ne.gain.setTargetAtTime(0,t,.004);n.connect(hp);hp.connect(ne);ne.connect(g);n.stop(t+.05);
  };
  S.bell=function(t,v){
    for(const dt of[0,.32]){
      const g=place(v);
      [[1320,1,1.4],[1985,.5,1],[2650,.35,.7],[3960,.15,.4]].forEach(function(m){
        const o=ctx.createOscillator(),e=ctx.createGain();o.frequency.value=m[0]*(dt?1.01:1);
        e.gain.setValueAtTime(m[1]*.05,t+dt);e.gain.setTargetAtTime(0,t+dt,m[2]/3);o.connect(e);e.connect(g);o.start(t+dt);o.stop(t+dt+m[2]*2);
      });
    }
  };
  S.car=function(t,v){
    const g=place(v),e=ctx.createGain();e.connect(g);
    const n=src(BROWN,t,true),lp=filt("lowpass",200);n.connect(lp);lp.connect(e);
    lp.frequency.setValueAtTime(180,t);lp.frequency.linearRampToValueAtTime(620,t+2);lp.frequency.linearRampToValueAtTime(160,t+4.5);
    e.gain.setValueAtTime(0,t);e.gain.linearRampToValueAtTime(.16,t+2);e.gain.linearRampToValueAtTime(0,t+4.5);n.stop(t+5);
  };
  S.doorOpen=function(t){                 /* the street comes in for a moment */
    S.street.gain.cancelScheduledValues(t);S.street.gain.setTargetAtTime(.2,t,.15);S.street.gain.setTargetAtTime(.07,t+2.2,.6);
  };
  S.setDuck=function(x){duck.gain.setTargetAtTime(x,ctx.currentTime,.25);};
  S.crowd=function(on){
    S.crowdOn=on;
    if(!on)S.voices.forEach(function(v){v.g.gain.cancelScheduledValues(ctx.currentTime);v.g.gain.setTargetAtTime(0,ctx.currentTime,.3);});
  };
  return S;
}
(async()=>{const SR=48000,DUR=19.4,CUT=4.2;
const off=new OfflineAudioContext(2,Math.round(SR*DUR),SR);
const S=ambBuild(off,off.destination);
/* outside: the street up front, the room behind glass */
S.street.gain.setValueAtTime(.3,0);S.street.gain.setValueAtTime(.3,CUT-.05);S.street.gain.setTargetAtTime(.07,CUT,.25);
S.car(.3,{g:.6,p:-.6});S.car(2.4,{g:.45,p:.5});
S.murmur(0,DUR);
S.voices.forEach(v=>{});                 // the walla runs throughout; the duck below muffles it outside
S.duck.gain.setValueAtTime(.35,0);S.duck.gain.setValueAtTime(.35,CUT-.02);S.duck.gain.linearRampToValueAtTime(1,CUT+.02);
/* inside */
S.bell(CUT+.05,{g:.45,p:.6});
S.grind(CUT+2.6,3.0,{g:.5,p:-.1});
S.knock(CUT+6.4,{g:.5,p:0});S.knock(CUT+6.62,{g:.5,p:0});
S.pump(CUT+7.2,8,{g:.45,p:0});
S.clink(CUT+9.8,{g:.7,p:.2});S.clink(CUT+12.4,{g:.6,p:-.4},.85);
const buf=await off.startRendering();
const L=buf.getChannelData(0),R=buf.getChannelData(1);let peak=0;for(let i=0;i<L.length;i++)peak=Math.max(peak,Math.abs(L[i]),Math.abs(R[i]));
const gain=Math.pow(10,-3/20)/peak;                  // -3 dBFS peak for the film
const fadeOut=Math.round(SR*1.2);
const n=L.length,ab=new ArrayBuffer(44+n*4),dv=new DataView(ab);
const w=(o,s)=>{for(let i=0;i<s.length;i++)dv.setUint8(o+i,s.charCodeAt(i));};
w(0,'RIFF');dv.setUint32(4,36+n*4,true);w(8,'WAVE');w(12,'fmt ');dv.setUint32(16,16,true);dv.setUint16(20,1,true);dv.setUint16(22,2,true);
dv.setUint32(24,SR,true);dv.setUint32(28,SR*4,true);dv.setUint16(32,4,true);dv.setUint16(34,16,true);w(36,'data');dv.setUint32(40,n*4,true);
for(let i=0;i<n;i++){const f=i>n-fadeOut?(n-i)/fadeOut:(i<SR*.3?i/(SR*.3):1);
  dv.setInt16(44+i*4,Math.max(-1,Math.min(1,L[i]*gain*f))*32767,true);dv.setInt16(46+i*4,Math.max(-1,Math.min(1,R[i]*gain*f))*32767,true);}
const u=new Uint8Array(ab);let s='';for(let i=0;i<u.length;i+=0x8000)s+=String.fromCharCode.apply(null,u.subarray(i,i+0x8000));
window.__dump=[{name:'trailer_sound.wav',b64:btoa(s)}];return 'peak '+peak.toFixed(3)+' gain '+gain.toFixed(2);})()
