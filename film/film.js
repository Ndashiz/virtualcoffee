// Frame-exact capture of Virtual Coffee for the trailer and the share image.
// Same server + injection as cdp.js, plus: requestAnimationFrame is taken over
// (the harness calls the loop itself, one frame per capture) and the clock
// advances by a FIXED step, so 30 captures are exactly one second of scene.
// usage: node film.js path.json   env: VC_ROOT OUT W H FPS WARM UI SEAT
//   path.json: {"fps":30,"shots":[{"keys":[{"t":0,"p":[x,y,z],"l":[x,y,z],"fov":45},...],
//               "hold":0,"doorOpen":[t0,t1]},...], "stills":[{"name":..,"frame":..}] }
//   (a bare {"keys":…} is one shot). Frames are numbered across shots: cuts.
const http=require('http'),fs=require('fs'),path=require('path'),{spawn}=require('child_process'),os=require('os');
const ROOT=process.env.VC_ROOT||(process.env.HOME+'/dev/virtualcoffee');
const OUT=process.env.OUT||'frames',W=+(process.env.W||1920),H=+(process.env.H||1080);
const SPEC=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const FPS=SPEC.fps||30;
const CH=process.env.CHROME||(process.env.HOME+'/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell');
const MIME={html:'text/html',js:'application/javascript',txt:'text/plain',png:'image/png',jpg:'image/jpeg',svg:'image/svg+xml',
  css:'text/css',woff2:'font/woff2',mp3:'audio/mpeg',json:'application/json',bin:'application/octet-stream',pdf:'application/pdf'};
function inject(h){
  const cam=`updateCamera(dt,t);
  if(window.__cam&&window.__cam.p){const c=window.__cam;camera.clearViewOffset();camera.position.set(c.p[0],c.p[1],c.p[2]);camera.up.set(0,1,0);camera.lookAt(c.l[0],c.l[1],c.l[2]);if(c.fov)camera.fov=c.fov;camera.updateProjectionMatrix();if(c.focus!==undefined){dofMat.uniforms.uFocus.value=c.focus;dofMat.uniforms.uRange.value=c.range||14;}}`;
  if(!h.includes('updateCamera(dt,t);'))throw new Error('no updateCamera');
  h=h.replace('updateCamera(dt,t);',cam);
  const clk='const raw=clock.getDelta(),dt=Math.min(raw,.05),t=clock.elapsedTime;';
  if(!h.includes(clk))throw new Error('no clock line');
  h=h.replace(clk,'const raw=clock.getDelta();let dt=Math.min(raw,.05);if(window.__fdt){dt=window.__fdt;clock.elapsedTime+=0;window.__ft=(window.__ft||clock.elapsedTime)+dt;clock.elapsedTime=window.__ft;}const t=clock.elapsedTime;');
  const names=['renderer','camera','scene','CAFE','QUALITY','THREE','openDoor','DOOR','dofMat','REAL','agents','GI','PROBE','SCAN'];
  const probe='window.__vc={};'+names.map(n=>`try{window.__vc.${n}=typeof ${n}!=="undefined"?${n}:null;}catch(e){}`).join('')+'\nanimate();\n})();';
  const tail='animate();\n})();',i=h.lastIndexOf(tail);
  h=h.slice(0,i)+probe+h.slice(i+tail.length);
  if(!process.env.UI)h=h.replace('</head>','<style>body>*:not(#app){visibility:hidden!important}</style></head>');
  return h;
}
const server=http.createServer((req,res)=>{
  let p=decodeURIComponent(new URL(req.url,'http://x').pathname);if(p.endsWith('/'))p+='index.html';
  if(p.includes('/api/vc/')){res.writeHead(200,{'content-type':'application/json'});return res.end('{"open":true}');}
  const f=path.join(ROOT,p);
  if(!f.startsWith(ROOT)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){res.writeHead(404);return res.end('nf');}
  let b=fs.readFileSync(f);if(p==='/index.html')b=Buffer.from(inject(b.toString('utf8')));
  res.writeHead(200,{'content-type':MIME[f.split('.').pop()]||'application/octet-stream'});res.end(b);
});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
// Catmull-Rom through keys (uniform in key index), eased per segment
function interp(keys,t){
  let i=0;while(i<keys.length-2&&t>keys[i+1].t)i++;
  const a=keys[Math.max(0,i-1)],b=keys[i],c=keys[i+1],d=keys[Math.min(keys.length-1,i+2)];
  let u=Math.min(1,Math.max(0,(t-b.t)/(c.t-b.t)));u=u*u*(3-2*u)*.35+u*.65;
  const cr=(p0,p1,p2,p3)=>p0.map((_,k)=>.5*((2*p1[k])+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u*u*u));
  return {p:cr(a.p,b.p,c.p,d.p),l:cr(a.l,b.l,c.l,d.l),fov:b.fov+(c.fov-b.fov)*u};
}
(async()=>{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));const sport=server.address().port;
  fs.mkdirSync(OUT,{recursive:true});
  const udd=fs.mkdtempSync(path.join(os.tmpdir(),'vcfilm-')),dport=9500+Math.floor(Math.random()*400);
  const chrome=spawn(CH,['--headless','--remote-debugging-port='+dport,'--user-data-dir='+udd,'--use-angle=swiftshader','--enable-unsafe-swiftshader',
    '--ignore-gpu-blocklist','--hide-scrollbars','--window-size='+W+','+H,'about:blank'],{stdio:'ignore'});
  let wsu=null;for(let k=0;k<100&&!wsu;k++){try{wsu=(await(await fetch(`http://127.0.0.1:${dport}/json/version`)).json()).webSocketDebuggerUrl;}catch(e){await sleep(100);}}
  const ws=new WebSocket(wsu);await new Promise(r=>ws.onopen=r);let id=0;const pend=new Map();
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id);}
    else if(m.method==='Runtime.exceptionThrown')console.log('[pageerror]',(m.params.exceptionDetails.exception||{}).description||'');};
  const send=(method,params={},sid)=>new Promise(r=>{const i=++id;pend.set(i,r);ws.send(JSON.stringify({id:i,method,params,sessionId:sid}));});
  const {result:{targetId}}=await send('Target.createTarget',{url:'about:blank'});
  const {result:{sessionId}}=await send('Target.attachToTarget',{targetId,flatten:true});
  const S=(m,p)=>send(m,p,sessionId);
  await S('Runtime.enable');await S('Page.enable');
  await S('Emulation.setDeviceMetricsOverride',{width:W,height:H,deviceScaleFactor:1,mobile:false});
  let pre="try{localStorage.setItem('vc:muted','1')}catch(e){}";
  if(process.env.SEAT)pre+="try{sessionStorage.setItem('vc:visit',JSON.stringify({t:Date.now(),heard:['profile'],outro:false,fem:false}))}catch(e){}";
  pre+="window.__rafQ=null;window.__rafFree=true;const __r=window.requestAnimationFrame.bind(window);"+
       "window.requestAnimationFrame=function(cb){if(window.__rafFree)return __r(cb);window.__rafQ=cb;return 1;};";
  await S('Page.addScriptToEvaluateOnNewDocument',{source:pre});
  const ev=async(x,aw)=>{const r=await S('Runtime.evaluate',{expression:x,awaitPromise:!!aw,returnByValue:true});
    if(r.result.exceptionDetails)throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0,400));return r.result.result.value;};
  const t0=Date.now();
  await S('Page.navigate',{url:`http://127.0.0.1:${sport}/index.html?fullres`});   // full resolution, whatever the frame rate
  for(;;){await sleep(500);let ok=false;try{ok=await ev('!!(window.__vc&&__vc.CAFE&&__vc.CAFE.ready)');}catch(e){}if(ok)break;if(Date.now()-t0>300000)throw new Error('never ready');}
  console.log('ready',((Date.now()-t0)/1000).toFixed(0)+'s');
  await sleep(+(process.env.WARM||30000));          // let bake, scans, people land (free-running loop)
  await ev('window.__rafFree=false;window.__fdt='+(1/FPS)+';0');
  await sleep(300);
  const shots=SPEC.shots||[SPEC];
  const stills=new Map((SPEC.stills||[]).map(s=>[s.frame,s.name]));
  const plan=[];
  for(const sh of shots){const k=sh.keys,T1=k[k.length-1].t+(sh.hold||0);
    for(let i=0,n=Math.round(T1*FPS);i<n;i++)plan.push({sh,t:i/FPS});}
  const N=plan.length;
  for(let f=0;f<N;f++){
    const {sh,t}=plan[f],keys=sh.keys,c=interp(keys,Math.min(t,keys[keys.length-1].t));
    const door=sh.doorOpen&&t>=sh.doorOpen[0]&&t<=sh.doorOpen[1]?'__vc.openDoor();':'';
    await ev(`window.__cam=${JSON.stringify(c)};${door}if(window.__rafQ){const q=window.__rafQ;window.__rafQ=null;q(performance.now());}0`);
    const {result:{data}}=await S('Page.captureScreenshot',{format:'png'});
    fs.writeFileSync(path.join(OUT,'f'+String(f).padStart(4,'0')+'.png'),Buffer.from(data,'base64'));
    if(stills.has(f))fs.copyFileSync(path.join(OUT,'f'+String(f).padStart(4,'0')+'.png'),path.join(OUT,stills.get(f)+'.png'));
    if(f%30===0)console.log('frame',f,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s');
  }
  try{await send('Browser.close');}catch(e){}await sleep(300);try{chrome.kill('SIGKILL');}catch(e){}
  server.close();fs.rmSync(udd,{recursive:true,force:true});console.log('done',N);process.exit(0);
})().catch(e=>{console.error('FATAL',e.message);process.exit(1);});
