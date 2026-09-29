// Runs in the page (PROBE=): exports the café's static interior for the Cycles bake.
// Fills window.__dump = [{name,text}|{name,b64}] which cdp.js writes to DUMP_DIR.
(async()=>{
const V=__vc,T=V.THREE,GI=V.GI;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<100&&!(GI&&GI.recv&&GI.recv.floor);i++)await sleep(100);
const recvOf=new Map();Object.keys(GI.recv).forEach(k=>{if(GI.recv[k])recvOf.set(GI.recv[k],k);});
const names=new Map();V.CAFE.meshes.forEach((m,k)=>names.set(m,k));
const cv=document.createElement('canvas');cv.width=cv.height=24;const cx=cv.getContext('2d',{willReadFrequently:true});
const avgCache=new Map();
function s2l(c){return c<=.04045?c/12.92:Math.pow((c+.055)/1.055,2.4);}
function texAvg(t){
  if(!t||!t.image)return null;
  if(avgCache.has(t))return avgCache.get(t);
  let r=null;
  try{cx.clearRect(0,0,24,24);cx.drawImage(t.image,0,0,24,24);const d=cx.getImageData(0,0,24,24).data;
    let a=[0,0,0],n=0;for(let i=0;i<d.length;i+=4){if(d[i+3]<8)continue;
      const f=t.encoding===T.sRGBEncoding?s2l:(x=>x);a[0]+=f(d[i]/255);a[1]+=f(d[i+1]/255);a[2]+=f(d[i+2]/255);n++;}
    if(n)r=[a[0]/n,a[1]/n,a[2]/n];}catch(e){}
  avgCache.set(t,r);return r;
}
const mats=new Map(),matList=[];
function matKey(m,mesh){
  // vertex-coloured materials get one entry per mesh (their average differs)
  const vc=m.vertexColors&&mesh.geometry.attributes.color;
  const key=vc?m.uuid+'|'+mesh.uuid:m.uuid;
  if(mats.has(key))return mats.get(key);
  const col=m.color?[m.color.r,m.color.g,m.color.b]:[1,1,1];
  const ma=texAvg(m.map);if(ma)for(let i=0;i<3;i++)col[i]*=ma[i];
  if(vc){const c=mesh.geometry.attributes.color.array;let a=[0,0,0];for(let i=0;i<c.length;i+=3){a[0]+=c[i];a[1]+=c[i+1];a[2]+=c[i+2];}
    const n=c.length/3;for(let i=0;i<3;i++)col[i]*=a[i]/n;}
  let em=[0,0,0];
  if(m.isMeshBasicMaterial){em=col.slice();}
  else if(m.emissive){const k=m.emissiveIntensity;em=[m.emissive.r*k,m.emissive.g*k,m.emissive.b*k];
    const ea=texAvg(m.emissiveMap);if(ea)for(let i=0;i<3;i++)em[i]*=ea[i];}
  const rec={id:matList.length,type:m.type,albedo:m.isMeshBasicMaterial?[0,0,0]:col,emit:em,
    rough:m.roughness!==undefined?m.roughness:1,metal:m.metalness||0,name:m.name||''};
  matList.push(rec);mats.set(key,rec.id);return rec.id;
}
const meshes=[],bins=[];
const _m=new T.Matrix4(),_n=new T.Matrix3(),v=new T.Vector3(),nn=new T.Vector3();
V.scene.updateMatrixWorld(true);
V.scene.traverse(o=>{
  if(!o.isMesh||o.isSkinnedMesh||o.isInstancedMesh)return;
  let vis=true,p=o;while(p){if(!p.visible){vis=false;break;}p=p.parent;}
  if(!vis||o.userData.outside)return;
  const m=Array.isArray(o.material)?o.material[0]:o.material;
  if(!m||m.isShaderMaterial||m.isRawShaderMaterial||m.isSpriteMaterial)return;
  if(m.blending!==T.NormalBlending)return;
  if(m.transparent&&m.opacity<.9)return;
  if(m.visible===false)return;
  const g=o.geometry,pa=g.attributes.position;if(!pa)return;
  const idx=g.index?g.index.array:null,nIdx=idx?idx.length:pa.count;
  if(nIdx<3)return;
  const bb=new T.Box3().setFromObject(o);
  if(bb.min.x>7.6||bb.max.x<-3.9||bb.min.z>4.4||bb.max.z<-5.4||bb.min.y>3.6)return;   // interior only
  const na=g.attributes.normal,uv2=recvOf.has(o)?g.attributes.uv2:null;
  // a receiver keeps only its faces that look INTO the room: the model's floor and
  // walls are slabs, and their far faces share the planar uv2 (they would overwrite
  // the texels of the faces we see)
  const INWARD={floor:[0,1,0],ceiling:[0,-1,0],backWall:[0,0,1],frontWall:[0,0,-1],leftWall:[1,0,0],shopWall:[-1,0,0]};
  const inw=uv2?INWARD[recvOf.get(o)]:null;
  _n.getNormalMatrix(o.matrixWorld);
  const P=[],Nn=[],Uu=[];
  const fn=new T.Vector3(),a=new T.Vector3(),b2=new T.Vector3(),c=new T.Vector3();
  for(let j=0;j<nIdx;j+=3){
    const ks=[0,1,2].map(q=>idx?idx[j+q]:j+q);
    a.fromBufferAttribute(pa,ks[0]).applyMatrix4(o.matrixWorld);b2.fromBufferAttribute(pa,ks[1]).applyMatrix4(o.matrixWorld);
    c.fromBufferAttribute(pa,ks[2]).applyMatrix4(o.matrixWorld);
    if(inw){fn.subVectors(b2,a).cross(new T.Vector3().subVectors(c,a)).normalize();
      if(fn.x*inw[0]+fn.y*inw[1]+fn.z*inw[2]<.7)continue;}
    for(const [q,k] of ks.entries()){
      const w=q===0?a:q===1?b2:c;P.push(w.x,w.y,w.z);
      if(na){nn.fromBufferAttribute(na,k).applyMatrix3(_n).normalize();Nn.push(nn.x,nn.y,nn.z);}else Nn.push(0,1,0);
      if(uv2)Uu.push(uv2.getX(k),uv2.getY(k));
    }
  }
  if(!P.length)return;
  const pos=new Float32Array(P),nrm=new Float32Array(Nn),uv=uv2?new Float32Array(Uu):null;
  const nOut=P.length/3;
  const mid=matKey(m,o);
  const name=(recvOf.get(o)?'RECV_'+recvOf.get(o):(names.get(o)||o.name||'mesh'))+'_'+meshes.length;
  meshes.push({name,mat:mid,verts:nOut,recv:recvOf.get(o)||null,bbox:[bb.min.x,bb.min.y,bb.min.z,bb.max.x,bb.max.y,bb.max.z]});
  bins.push(pos,nrm);if(uv)bins.push(uv);
});
const lights=[];
V.scene.traverse(o=>{
  if(!o.isLight||o.isAmbientLight||o.isHemisphereLight||o.isLightProbe)return;
  let vis=true,p=o;while(p){if(!p.visible){vis=false;break;}p=p.parent;}
  if(!vis||!(o.intensity>0))return;
  const w=new T.Vector3();o.getWorldPosition(w);
  if(!o.isDirectionalLight&&(w.x>7.6||w.x<-3.9||w.z>4.4||w.z<-5.4||w.y>3.6))return;
  const L={type:o.type,pos:[w.x,w.y,w.z],color:[o.color.r,o.color.g,o.color.b],intensity:o.intensity,
    distance:o.distance||0,decay:o.decay===undefined?2:o.decay};
  if(o.target){const t=new T.Vector3();o.target.getWorldPosition(t);L.target=[t.x,t.y,t.z];}
  if(o.isSpotLight){L.angle=o.angle;L.penumbra=o.penumbra;}
  lights.push(L);
});
// pack
function b64(f32){const u=new Uint8Array(f32.buffer,f32.byteOffset,f32.byteLength);let s='';const C=0x8000;
  for(let i=0;i<u.length;i+=C)s+=String.fromCharCode.apply(null,u.subarray(i,i+C));return btoa(s);}
let total=0;bins.forEach(b=>total+=b.length);
const all=new Float32Array(total);let o=0;bins.forEach(b=>{all.set(b,o);o+=b.length;});
const out=[{name:'header.json',text:JSON.stringify({meshes,materials:matList,lights,room:{x0:-3.38,x1:7.09,z0:-4.88,z1:3.94,h:3.44},
  floats:total})}];
const CH=4*1024*1024;   // floats per chunk
for(let i=0,k=0;i<total;i+=CH,k++)out.push({name:'geo.'+String(k).padStart(3,'0')+'.bin',b64:b64(all.subarray(i,Math.min(total,i+CH)))});
window.__dump=out;
return 'meshes '+meshes.length+' verts '+meshes.reduce((a,m)=>a+m.verts,0)+' mats '+matList.length+' lights '+lights.length+
  ' recv '+meshes.filter(m=>m.recv).map(m=>m.recv).join(',')+' chunks '+(out.length-1);
})()
