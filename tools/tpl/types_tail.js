
/* ---------- scene ---------- */
var canvas=$('c'),renderer;
try{ renderer=new THREE.WebGLRenderer({canvas:canvas,antialias:true}); }
catch(e){ $('err').textContent='這個瀏覽器無法啟用 3D 繪圖（WebGL）。'; $('err').style.display='flex'; return; }
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
var scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,1,0.1,300);
(function(){ var cv=document.createElement('canvas'); cv.width=4; cv.height=256; var g=cv.getContext('2d'),gr=g.createLinearGradient(0,0,0,256);
  gr.addColorStop(0,'#9cc9ea'); gr.addColorStop(.6,'#d8e9f2'); gr.addColorStop(1,'#eef3ee'); g.fillStyle=gr; g.fillRect(0,0,4,256); scene.background=new THREE.CanvasTexture(cv); })();
scene.fog=new THREE.Fog(0xdde8ec,30,90);
scene.add(new THREE.HemisphereLight(0xffffff,0x7c8a70,0.9));
var sun=new THREE.DirectionalLight(0xfff3dc,0.85); sun.position.set(7,12,5); sun.castShadow=true; sun.shadow.mapSize.set(2048,2048);
var sc=sun.shadow.camera; sc.left=-9; sc.right=9; sc.top=9; sc.bottom=-9; sc.near=1; sc.far=40; sun.shadow.bias=-0.0006; scene.add(sun);
(function(){ var t=tex('grass'); t.repeat.set(60,60); var m=new THREE.Mesh(new THREE.CircleGeometry(90,48),std(0xdde6cf,{map:t})); m.rotation.x=-Math.PI/2; m.receiveShadow=true; scene.add(m); })();
var dirty=true; function redraw(){ dirty=true; }

/* state the borrowed builders expect */
var S={tent:null,rot:0,tx:0,tz:0,xray:false,margin:60,labels:false,ropes:true,wx:'sunny',mode:'single',pg:'m',ph:170,sL:40,sW:40,siteType:'grass'};
var WX={sunny:{}},siteY=0,areaNo=0;
var tentG=new THREE.Group(),extraG=new THREE.Group(),personG=new THREE.Group(),tentMeshes=[],outlineMat=null,ropeMat=null,shellMat=null,zoneMat=null,ropeObjs=[];
scene.add(tentG,extraG,personG);
function isArea(){ return false; }
function placeTent(){ tentG.position.set(0,0,0); tentG.rotation.y=0; }

/* ---------- types that the simulator does not have ---------- */
function clearG(g){ while(g.children.length){ var o=g.children[0]; g.remove(o); dispose(o); } }
function ropePeg(g,a,b){
  g.add(limb(a,P(b.x,.035,b.z),.008,.008,new THREE.MeshStandardMaterial({color:0xffb300,emissive:0x7a5200,roughness:.6}),6));
  var d=P(b.x,.035,b.z).sub(a).normalize(),gp=P(b.x,.035,b.z); g.add(limb(gp.clone().addScaledVector(d,.1),gp.clone().addScaledVector(d,-.1).setY(.11),.011,.011,std(0xd8d8d2,{metalness:.6,roughness:.4}),6));
}
function fabric(col,o){ var p={color:col,roughness:.9,side:THREE.DoubleSide}; if(o) for(var k in o) p[k]=o[k]; return new THREE.MeshStandardMaterial(p); }
function buildRooftop(m){
  var g=extraG,L=m.L/100,W=m.W/100,H=m.H/100,by=1.83,cx=-.35,x0=cx-L/2,x1=cx+L/2,hw=W/2;
  var c=car('suv'); g.add(c);
  var rack=std(0x2a2d2f,{metalness:.5,roughness:.5}),shellM=std(0x2f3336,{roughness:.45,metalness:.3}),fab=fabric(m.color);
  [-.55,.55].forEach(function(dx){ var bar=new THREE.Mesh(new THREE.BoxGeometry(.06,.05,W+.2),rack); bar.position.set(cx+dx,by-.07,0); g.add(bar); });
  var base=new THREE.Mesh(new THREE.BoxGeometry(L,.1,W),shellM); base.position.set(cx,by,0); base.castShadow=true; g.add(base);
  var top=by+.05,lidLen=Math.hypot(L,H),lid=new THREE.Mesh(new THREE.BoxGeometry(lidLen,.06,W+.04),shellM); lid.position.set(cx,top+H/2,0); lid.rotation.z=-Math.atan2(H,L); lid.castShadow=true; g.add(lid);
  /* hinge at the front (x1); the tall open end is at the rear (x0); ladder on the side */
  var tri=[]; [hw,-hw].forEach(function(z){ tri.push(P(x1,top,z),P(x0,top,z),P(x0,top+H-.04,z)); });
  tri.push(P(x0,top,-hw),P(x0,top,hw),P(x0,top+H-.04,hw),P(x0,top,-hw),P(x0,top+H-.04,hw),P(x0,top+H-.04,-hw));
  var tg=new THREE.BufferGeometry().setFromPoints(tri); tg.computeVertexNormals(); var tm=new THREE.Mesh(tg,fab); tm.castShadow=true; g.add(tm);
  var win=fabric(0x262b27,{transparent:true,opacity:.8});
  g.add(quad(P(x0-.012,top+.12,-hw*.6),P(x0-.012,top+.12,hw*.6),P(x0-.012,top+H*.72,hw*.6),P(x0-.012,top+H*.72,-hw*.6),win));
  [1,-1].forEach(function(sg){ var z=sg*(hw+.012); g.add(quad(P(x0+.75,top+.1,z),P(x0+.12,top+.1,z),P(x0+.12,top+H*.5,z),P(x0+.5,top+H*.38,z),win)); });
  var lm=std(0xb9bec2,{metalness:.7,roughness:.35}),lx=x0+.42,a=P(lx,top-.03,hw+.03),b=P(lx,0,hw+.95),i;
  [1,-1].forEach(function(sg){ g.add(limb(P(a.x+sg*.2,a.y,a.z),P(b.x+sg*.2,b.y,b.z),.018,.018,lm,8)); });
  for(i=1;i<7;i++){ var k=i/7.4,q=a.clone().lerp(b,k); g.add(limb(P(q.x-.2,q.y,q.z),P(q.x+.2,q.y,q.z),.014,.014,lm,6)); }
}

/* ---------- show one type ---------- */
var cam={az:.75,el:.34,r:10,target:new THREE.Vector3(0,.9,0)},spin=true,cur=null;
function show(t){
  cur=t; clearG(extraG); clearG(tentG); tentMeshes=[];
  var m=t.m,L=m.L/100,W=m.W/100,H=m.H/100,px=L/2+.5,pz=-(W/2+.5),top=H;
  if(m.shape){
    S.tent={id:t.id,brand:'',name:t.name,L:m.L,W:m.W,H:m.H,shape:m.shape,color:m.color,inner:m.inner,wall:m.wall};
    buildTent1();
    [outlineMat,ropeMat,zoneMat].forEach(function(x){ if(x) x.visible=false; });
    tentG.traverse(function(o){ if(o.geometry&&o.geometry.type==='RingGeometry') o.visible=false; });
    if(t.car){ var c=car('suv'); c.rotation.y=Math.PI/2; c.position.set(-L/2-1.0,0,0); extraG.add(c); }
  }else if(t.id==='rooftop'){ buildRooftop(m); px=1.2; pz=-1.75; top=3.0; L=4.6; W=1.9; }
  buildPerson(); personG.position.set(px,0,pz); personG.rotation.y=Math.PI/4;
  var span=Math.max(L,W,top*1.6)+(t.car?2.2:0);
  cam.r=Math.max(7.5,span*1.75+2.2)*(camera.aspect<.9?1.25:1); cam.target.set(t.car?-.9:0,Math.min(1.3,top*.42),0);
  $('tag').textContent='人物身高 170 cm';
  var cta=$('cta'); if(t.id==='rooftop'){ cta.href='index.html'; cta.textContent='前往搭設模擬（車頂帳不在模擬範圍）→'; } else { cta.href='index.html#type-'+t.id; cta.textContent='用搭設模擬看這頂放不放得下 →'; }
  $('tName').textContent=t.name; $('tLead').textContent=t.lead; $('tFit').textContent=t.fit;
  var sp=$('tSpecs'); sp.textContent=''; [['常見尺寸',t.size],['適合人數',t.cap],['搭設時間',t.time],['搭設人數',t.crew]].forEach(function(x){ var d=document.createElement('div'),a=document.createElement('dt'),b=document.createElement('dd'); a.textContent=x[0]; b.textContent=x[1]; d.appendChild(a); d.appendChild(b); sp.appendChild(d); });
  var rt=$('tRates'); rt.textContent=''; ASPECTS.forEach(function(a,i){ var row=document.createElement('div'),lab=document.createElement('span'),bar=document.createElement('span'),k; row.className='rate'; lab.textContent=a; bar.className='bar'; bar.setAttribute('role','img'); bar.setAttribute('aria-label',a+' '+t.r[i]+' 分，滿分 5 分');
    for(k=1;k<=5;k++){ var s=document.createElement('i'); if(k<=t.r[i]) s.className='on'; bar.appendChild(s); } row.appendChild(lab); row.appendChild(bar); rt.appendChild(row); });
  [['tPros',t.pros],['tCons',t.cons]].forEach(function(x){ var ul=$(x[0]); ul.textContent=''; x[1].forEach(function(s){ var li=document.createElement('li'); li.textContent=s; ul.appendChild(li); }); });
  Array.prototype.forEach.call($('types').children,function(b){ b.setAttribute('aria-pressed',String(b.dataset.id===t.id)); });
  redraw();
}
TYPES.forEach(function(t){ var b=document.createElement('button'); b.type='button'; b.textContent=t.name; b.dataset.id=t.id; b.addEventListener('click',function(){ show(t); }); $('types').appendChild(b); });

/* ---------- camera + pointer ---------- */
function applyCam(){ var ce=Math.cos(cam.el); camera.position.set(cam.target.x+cam.r*ce*Math.sin(cam.az),cam.target.y+cam.r*Math.sin(cam.el),cam.target.z+cam.r*ce*Math.cos(cam.az)); camera.lookAt(cam.target); }
function resize(){ var w=canvas.clientWidth,h=canvas.clientHeight; if(!w||!h) return; renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix(); redraw(); }
if(window.ResizeObserver) new ResizeObserver(resize).observe(canvas.parentElement); else window.addEventListener('resize',resize);
var ptrs=new Map(),last={x:0,y:0},pinch={d:1,r:1};
function pdist(){ var a=Array.from(ptrs.values()); return Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)||1; }
canvas.addEventListener('pointerdown',function(e){ try{canvas.setPointerCapture(e.pointerId)}catch(_){ } ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY}); last.x=e.clientX; last.y=e.clientY; if(ptrs.size===2){ pinch.d=pdist(); pinch.r=cam.r; } setSpin(false); });
canvas.addEventListener('pointermove',function(e){ if(!ptrs.has(e.pointerId)) return; ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(ptrs.size===1){ cam.az-=(e.clientX-last.x)*0.008; cam.el=Math.min(1.5,Math.max(0.05,cam.el+(e.clientY-last.y)*0.006)); last.x=e.clientX; last.y=e.clientY; redraw(); }
  else if(ptrs.size===2){ cam.r=Math.min(40,Math.max(3,pinch.r*pinch.d/pdist())); redraw(); } });
function pend(e){ ptrs.delete(e.pointerId); if(ptrs.size===1){ var p=Array.from(ptrs.values())[0]; last.x=p.x; last.y=p.y; } }
canvas.addEventListener('pointerup',pend); canvas.addEventListener('pointercancel',pend);
canvas.addEventListener('wheel',function(e){ e.preventDefault(); cam.r=Math.min(40,Math.max(3,cam.r*Math.exp(e.deltaY*0.0012))); redraw(); },{passive:false});
function setSpin(v){ spin=v; var b=$('spin'); b.setAttribute('aria-pressed',String(v)); b.textContent='自動旋轉：'+(v?'開':'關'); }
$('spin').addEventListener('click',function(){ setSpin(!spin); });
if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches) setSpin(false);

resize(); show(TYPES[0]);
var lastT=0;
(function loop(t){ var dt=Math.min(.05,((t||0)-lastT)/1000); lastT=t||0; if(spin){ cam.az+=dt*.22; dirty=true; } if(dirty){ dirty=false; applyCam(); renderer.render(scene,camera); } requestAnimationFrame(loop); })();
})();
</script>
</body>
</html>
