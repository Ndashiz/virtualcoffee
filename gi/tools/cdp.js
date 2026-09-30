// Headless renderer for Virtual Coffee without Playwright: a tiny static server
// (with the same index.html injection as .work/characters/tools/shoot.js) and
// chrome-headless-shell driven over the DevTools protocol.
// usage: node cdp.js specs.json   env: VC_ROOT OUT W H UI SEAT TOUCH RM WARM PROBE EXPOSE STATS QUERY DUMP_DIR CHROME
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process'), os = require('os');
const ROOT = process.env.VC_ROOT || (process.env.HOME + '/dev/virtualcoffee');
const OUT = process.env.OUT || 'shots';
const W = +(process.env.W || 1440), H = +(process.env.H || 810);
const specs = JSON.parse(fs.readFileSync(process.argv[2] || '/dev/null', 'utf8') || '[]');
const CHROME = process.env.CHROME || (process.env.HOME + '/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell');
const MIME = { html:'text/html', js:'application/javascript', txt:'text/plain', png:'image/png', jpg:'image/jpeg',
  svg:'image/svg+xml', css:'text/css', woff2:'font/woff2', mp3:'audio/mpeg', json:'application/json', m4a:'audio/mp4',
  obj:'text/plain', pdf:'application/pdf', bin:'application/octet-stream' };

function inject(html){
  const hookCam = `updateCamera(dt,t);
  if(window.__cam&&window.__cam.p){const c=window.__cam;camera.clearViewOffset();camera.position.set(c.p[0],c.p[1],c.p[2]);camera.up.set(0,1,0);camera.lookAt(c.l[0],c.l[1],c.l[2]);if(c.fov&&camera.fov!==c.fov){camera.fov=c.fov;}camera.updateProjectionMatrix();}`;
  if(!html.includes('updateCamera(dt,t);')) throw new Error('hook: updateCamera not found');
  html = html.replace('updateCamera(dt,t);', hookCam);
  html = html.replace('function animate(){\n  requestAnimationFrame(animate);',
    'function animate(){\n  requestAnimationFrame(animate);window.__frames=(window.__frames||0)+1;');
  const names = ['renderer','camera','scene','CAFE','guest','QUALITY','THREE','closeCafe','JB','ATL','pendants','jbPlayTrack',
    'aoMat','dofMat','STREET','skyMat','SKY','skyHero','REAL','HERO','agents','TVS','READABLES','SHOTS','MATS','LM','applyLightMaps','GI','ceil','PROBE',
    ...(process.env.EXPOSE||'').split(',').filter(Boolean)];
  const probe = 'window.__vc={};' + names.map(n=>`try{window.__vc.${n}=typeof ${n}!=="undefined"?${n}:null;}catch(e){}`).join('') + '\nanimate();\n})();';
  const tail = 'animate();\n})();';
  const i = html.lastIndexOf(tail);
  if(i<0) throw new Error('hook: animate tail not found');
  html = html.slice(0,i) + probe + html.slice(i+tail.length);
  if(!process.env.UI) html = html.replace('</head>', '<style>body>*:not(#app){visibility:hidden!important}</style></head>');
  return html;
}
const server = http.createServer((req,res)=>{
  let p = decodeURIComponent(new URL(req.url,'http://x').pathname); if(p.endsWith('/')) p += 'index.html';
  if(p.includes('/api/vc/')){res.writeHead(200,{'content-type':'application/json'});return res.end('{"open":true}');}
  const f = path.join(ROOT, p);
  if(!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){res.writeHead(404);return res.end('nf');}
  let body = fs.readFileSync(f);
  if(p === '/index.html') body = Buffer.from(inject(body.toString('utf8')));
  res.writeHead(200,{'content-type':MIME[f.split('.').pop()]||'application/octet-stream','cache-control':'no-store'});
  res.end(body);
});
const sleep = ms => new Promise(r=>setTimeout(r,ms));
(async()=>{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const sport = server.address().port;
  fs.mkdirSync(OUT,{recursive:true});
  const udd = fs.mkdtempSync(path.join(os.tmpdir(),'vccdp-'));
  const dport = 9300 + Math.floor(Math.random()*500);
  const chrome = spawn(CHROME,['--headless','--remote-debugging-port='+dport,'--user-data-dir='+udd,
    '--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required',
    '--no-first-run','--hide-scrollbars','--window-size='+W+','+H,'about:blank'],{stdio:['ignore','ignore','pipe']});
  let wsUrl=null;
  for(let k=0;k<100&&!wsUrl;k++){ try{ const j=await (await fetch(`http://127.0.0.1:${dport}/json/version`)).json(); wsUrl=j.webSocketDebuggerUrl; }catch(e){ await sleep(100); } }
  if(!wsUrl) throw new Error('chrome did not start');
  const ws = new WebSocket(wsUrl); await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
  let id=0; const pend=new Map(); const handlers=[];
  ws.onmessage = ev => { const m=JSON.parse(ev.data); if(m.id&&pend.has(m.id)){const {res,rej}=pend.get(m.id);pend.delete(m.id);m.error?rej(new Error(JSON.stringify(m.error))):res(m.result);} else handlers.forEach(h=>h(m)); };
  const send = (method,params={},sessionId)=>new Promise((res,rej)=>{const i=++id;pend.set(i,{res,rej});ws.send(JSON.stringify({id:i,method,params,sessionId}));});
  const {targetId} = await send('Target.createTarget',{url:'about:blank'});
  const {sessionId} = await send('Target.attachToTarget',{targetId,flatten:true});
  const S = (m,p)=>send(m,p,sessionId);
  handlers.push(m=>{
    if(m.method==='Runtime.consoleAPICalled'){const t=m.params.args.map(a=>a.value!==undefined?String(a.value):(a.description||'')).join(' ');
      if(/error|warn|\[vc\]/i.test(t)&&!/deprecated/i.test(t)) console.log('[page]',t.slice(0,400));}
    if(m.method==='Runtime.exceptionThrown'){const d=m.params.exceptionDetails;console.log('[pageerror]',(d.exception&&d.exception.description||d.text).slice(0,600));}
  });
  await S('Runtime.enable'); await S('Page.enable');
  await S('Emulation.setDeviceMetricsOverride',{width:W,height:H,deviceScaleFactor:1,mobile:!!process.env.TOUCH});
  if(process.env.TOUCH) await S('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:5});
  if(process.env.RM) await S('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  let pre = "try{localStorage.setItem('vc:muted','1')}catch(e){}";
  if(process.env.SEAT) pre += "try{sessionStorage.setItem('vc:visit',JSON.stringify({t:Date.now(),heard:['profile'],outro:false,fem:false}))}catch(e){}";
  await S('Page.addScriptToEvaluateOnNewDocument',{source:pre});
  const ev = async (expr,awaitPromise)=>{const r=await S('Runtime.evaluate',{expression:expr,awaitPromise:!!awaitPromise,returnByValue:true});
    if(r.exceptionDetails) throw new Error((r.exceptionDetails.exception&&r.exceptionDetails.exception.description)||r.exceptionDetails.text); return r.result.value;};
  const t0=Date.now();
  await S('Page.navigate',{url:`http://127.0.0.1:${sport}/index.html${process.env.QUERY?process.env.QUERY+'&':'?'}fullres`});   // no resolution governor: 5 fps in software is not a reason to render small
  for(;;){ await sleep(500); let ok=false; try{ok=await ev('!!(window.__vc&&__vc.CAFE&&__vc.CAFE.ready)');}catch(e){} if(ok)break; if(Date.now()-t0>240000) throw new Error('model never ready'); }
  console.log('model ready in',((Date.now()-t0)/1000).toFixed(1),'s; quality',await ev('__vc.QUALITY.name'));
  if(process.env.WARM) await sleep(+process.env.WARM);
  if(process.env.PROBE) console.log(await ev(fs.readFileSync(process.env.PROBE,'utf8'),true));
  if(process.env.DUMP_DIR){
    fs.mkdirSync(process.env.DUMP_DIR,{recursive:true});
    const n=await ev('(window.__dump||[]).length');
    for(let i=0;i<n;i++){
      const it=await ev(`window.__dump[${i}]`);
      const f=path.join(process.env.DUMP_DIR,it.name);
      if(it.text!==undefined)fs.writeFileSync(f,it.text);else fs.writeFileSync(f,Buffer.from(it.b64,'base64'));
    }
    console.log('dumped',n,'files to',process.env.DUMP_DIR);
  }
  for(const s of specs){
    await ev(`window.__cam=${JSON.stringify(s)};${s.eval||''}`);
    const f0 = await ev('window.__frames||0');
    for(;;){ await sleep(200); if((await ev('window.__frames||0'))>=f0+(s.frames||4)) break; }
    const {data} = await S('Page.captureScreenshot',{format:'png'});
    fs.writeFileSync(path.join(OUT,s.name+'.png'),Buffer.from(data,'base64'));
    console.log('shot',s.name,((Date.now()-t0)/1000).toFixed(1)+'s');
  }
  if(process.env.STATS) console.log(await ev('JSON.stringify(__vc.renderer.info.render)+" "+JSON.stringify(__vc.renderer.info.memory)'));
  try{await send('Browser.close');}catch(e){}
  await sleep(300); try{chrome.kill('SIGKILL');}catch(e){}
  server.close(); fs.rmSync(udd,{recursive:true,force:true});
  process.exit(0);
})().catch(e=>{console.error('FATAL',e.message);process.exit(1);});
