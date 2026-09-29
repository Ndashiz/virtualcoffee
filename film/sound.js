(async()=>{const V=__vc;const SR=48000,DUR=19.4,CUT=4.2;
const off=new OfflineAudioContext(2,Math.round(SR*DUR),SR);
const S=V.ambBuild(off,off.destination);
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
