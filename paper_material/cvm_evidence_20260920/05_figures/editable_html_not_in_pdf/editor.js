buildA(d);buildG(d);buildFB(d);
// Match the narrow serif labels while retaining real selectable SVG text.
for(const n of nodes.values())for(const t of n.element.querySelectorAll('text')){
 const width=t.getComputedTextLength();
 if(width>n.w-12&&!t.hasAttribute('textLength')){t.setAttribute('textLength',n.w-12);t.setAttribute('lengthAdjust','spacingAndGlyphs');}
}
const original={nodes:Object.fromEntries([...nodes].map(([id,n])=>[id,[0,0]])),edges:Object.fromEntries([...edges].map(([id,e])=>[id,e.points.map(p=>[...p])]))};
const storeKey='gcdl-muted-1to1:v1:'+location.pathname+':'+(document.querySelector('#saved-state').dataset.revision||'base');
let selection=null,drag=null,undoStack=[],editing=false,scale=1,savedNoticeTimer;
const message=document.querySelector('#message'),undoButton=document.querySelector('#undo');
function tell(s){message.textContent=s;}
function snapshot(){return {nodes:Object.fromEntries([...nodes].map(([id,n])=>[id,[n.dx,n.dy]])),edges:Object.fromEntries([...edges].map(([id,e])=>[id,e.points.map(p=>[...p])]))};}
function validState(v){return v&&v.nodes&&v.edges&&Object.keys(v.nodes).length===nodes.size&&Object.keys(v.edges).length===edges.size&&[...nodes.keys()].every(id=>Array.isArray(v.nodes[id])&&v.nodes[id].length===2&&v.nodes[id].every(Number.isFinite))&&[...edges.keys()].every(id=>Array.isArray(v.edges[id])&&v.edges[id].length>=2&&v.edges[id].every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)));}
function restore(v){if(!validState(v))return false;for(const[id,n]of nodes){[n.dx,n.dy]=v.nodes[id];n.element.setAttribute('transform',`translate(${n.dx} ${n.dy})`);}for(const[id,e]of edges){e.points=v.edges[id].map(p=>[...p]);renderEdge(e);}drawHandles();return true;}
function save(){try{localStorage.setItem(storeKey,JSON.stringify(snapshot()));tell('修改已自动保存');}catch{tell('浏览器无法保存，可导出 HTML 保留修改');}undoButton.disabled=!undoStack.length;}
function pushUndo(s=snapshot()){undoStack.push(s);if(undoStack.length>80)undoStack.shift();undoButton.disabled=false;}
function point(evt){const p=new DOMPoint(evt.clientX,evt.clientY);return p.matrixTransform(svg.getScreenCTM().inverse());}
function select(type,id){selection={type,id};for(const n of nodes.values())n.element.classList.toggle('selected',type==='node'&&n.id===id);for(const e of edges.values())e.element.classList.toggle('selected',type==='edge'&&e.id===id);document.querySelector('#straight').disabled=type!=='edge';document.querySelector('#restore-one').disabled=false;drawHandles();}
function clearSelection(){selection=null;nodes.forEach(n=>n.element.classList.remove('selected'));edges.forEach(e=>e.element.classList.remove('selected'));document.querySelector('#straight').disabled=true;document.querySelector('#restore-one').disabled=true;drawHandles();}
function drawHandles(){handleLayer.replaceChildren();if(!editing||selection?.type!=='edge')return;const e=edges.get(selection.id);e.points.forEach((p,i)=>el('circle',{cx:p[0],cy:p[1],r:5.5,'class':'point-handle','data-index':i,tabindex:0,role:'button','aria-label':'连接点 '+(i+1)},handleLayer));for(let i=0;i<e.points.length-1;i++){const a=e.points[i],b=e.points[i+1];if(Math.hypot(a[0]-b[0],a[1]-b[1])<26)continue;el('rect',{x:(a[0]+b[0])/2-3.5,y:(a[1]+b[1])/2-3.5,width:7,height:7,'class':'mid-handle','data-mid':i},handleLayer);}}
function moveNode(id,dx,dy,from){const n=nodes.get(id),[oldx,oldy]=from.nodes[id];n.dx=oldx+dx;n.dy=oldy+dy;n.element.setAttribute('transform',`translate(${n.dx} ${n.dy})`);for(const[eid,e]of edges){let pts=from.edges[eid].map(p=>[...p]);for(const[end,bound]of [[0,e.opts.source],[pts.length-1,e.opts.target]])if(bound===id){const near=end===0?1:end-1;const old=from.edges[eid][end],oldNear=from.edges[eid][near];pts[end]=[old[0]+dx,old[1]+dy];if(pts.length>2){if(Math.abs(old[0]-oldNear[0])<.01)pts[near][0]+=dx;else if(Math.abs(old[1]-oldNear[1])<.01)pts[near][1]+=dy;}}e.points=pts;renderEdge(e);}}
svg.addEventListener('pointerdown',event=>{
 if(!editing||event.button!==0)return;const p=point(event),handle=event.target.closest('[data-index],[data-mid]'),node=event.target.closest('[data-node]'),edge=event.target.closest('[data-edge]');
 if(handle&&selection?.type==='edge'){
  const before=snapshot(),e=edges.get(selection.id);let index=Number(handle.dataset.index);
  if(handle.hasAttribute('data-mid')){index=Number(handle.dataset.mid)+1;e.points.splice(index,0,[p.x,p.y]);}
  drag={type:'point',id:e.id,index,start:p,pointOrigin:[...e.points[index]],before};
 }else if(node){select('node',node.dataset.node);drag={type:'node',id:node.dataset.node,start:p,before:snapshot()};}
 else if(edge){select('edge',edge.dataset.edge);tell('拖动圆点调整连接；拖动小方块增加拐点');return;}
 else{clearSelection();return;}
 event.preventDefault();svg.setPointerCapture(event.pointerId);
});
svg.addEventListener('pointermove',event=>{
 if(!drag)return;const p=point(event);let dx=p.x-drag.start.x,dy=p.y-drag.start.y;
 if(event.shiftKey){if(Math.abs(dx)>Math.abs(dy))dy=0;else dx=0;}
 if(drag.type==='node')moveNode(drag.id,dx,dy,drag.before);
 else{const e=edges.get(drag.id);e.points[drag.index]=[Math.max(0,Math.min(1448,drag.pointOrigin[0]+dx)),Math.max(0,Math.min(1086,drag.pointOrigin[1]+dy))];renderEdge(e);drawHandles();}
});
function finishDrag(event,cancel=false){if(!drag)return;if(cancel)restore(drag.before);else{if(JSON.stringify(snapshot())!==JSON.stringify(drag.before)){pushUndo(drag.before);save();}}drag=null;drawHandles();if(svg.hasPointerCapture(event.pointerId))svg.releasePointerCapture(event.pointerId);}
svg.addEventListener('pointerup',event=>finishDrag(event));svg.addEventListener('pointercancel',event=>finishDrag(event,true));
document.querySelector('#edit').addEventListener('change',event=>{editing=event.target.checked;document.body.classList.toggle('editing',editing);clearSelection();tell(editing?'拖动模块或选择连线；Shift 可限制移动方向':'按原图布局查看 · 1448 × 1086');});
document.querySelector('#straight').onclick=()=>{if(selection?.type!=='edge')return;pushUndo();const e=edges.get(selection.id);e.points=[e.points[0],e.points.at(-1)];renderEdge(e);drawHandles();save();};
document.querySelector('#restore-one').onclick=()=>{if(!selection)return;pushUndo();if(selection.type==='edge'){const e=edges.get(selection.id),base=original.edges[e.id];e.points=base.map(p=>[...p]);for(const[end,bound]of [[0,e.opts.source],[e.points.length-1,e.opts.target]])if(nodes.has(bound)){const n=nodes.get(bound),near=end===0?1:end-1;e.points[end][0]+=n.dx;e.points[end][1]+=n.dy;if(e.points.length>2){if(Math.abs(base[end][0]-base[near][0])<.01)e.points[near][0]+=n.dx;else if(Math.abs(base[end][1]-base[near][1])<.01)e.points[near][1]+=n.dy;}}renderEdge(e);}else{const n=nodes.get(selection.id);moveNode(n.id,-n.dx,-n.dy,snapshot());}drawHandles();save();};
undoButton.onclick=()=>{if(undoStack.length){restore(undoStack.pop());save();}};
document.querySelector('#reset').onclick=()=>{pushUndo();restore(original);clearSelection();save();};
document.addEventListener('keydown',event=>{
 if(event.key==='Escape'){if(drag){restore(drag.before);drag=null;}document.body.classList.remove('clean');clearSelection();return;}
 if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='z'&&editing){event.preventDefault();undoButton.click();return;}
 if(!editing||!selection||!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(event.key))return;
 const step=event.shiftKey?1:5,dx=event.key==='ArrowLeft'?-step:event.key==='ArrowRight'?step:0,dy=event.key==='ArrowUp'?-step:event.key==='ArrowDown'?step:0;
 if(selection.type==='node'){event.preventDefault();const before=snapshot();moveNode(selection.id,dx,dy,before);pushUndo(before);save();}
 else if(document.activeElement?.hasAttribute('data-index')){event.preventDefault();const e=edges.get(selection.id),i=Number(document.activeElement.dataset.index);pushUndo();e.points[i][0]+=dx;e.points[i][1]+=dy;renderEdge(e);drawHandles();handleLayer.querySelector(`[data-index="${i}"]`)?.focus();save();}
});
function zoom(value){scale=Math.max(.3,Math.min(3,value));svg.style.width=(1448*scale)+'px';svg.style.height=(1086*scale)+'px';document.querySelector('#zoom-label').textContent=Math.round(scale*100)+'%';}
function fit(){zoom(Math.min(1,(document.querySelector('#viewport').clientWidth-24)/1448));}
document.querySelector('#fit').onclick=fit;document.querySelector('#actual').onclick=()=>zoom(1);
document.querySelector('#minus').onclick=()=>zoom(scale-.1);document.querySelector('#plus').onclick=()=>zoom(scale+.1);
document.querySelector('#clean').onclick=()=>{document.body.classList.toggle('clean');clearSelection();};
function download(blob,name){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function cleanSVG(){const clone=svg.cloneNode(true);clone.querySelector('#handles')?.remove();clone.querySelectorAll('.edge-hit').forEach(n=>n.remove());clone.querySelectorAll('.selected').forEach(n=>n.classList.remove('selected'));clone.removeAttribute('style');clone.setAttribute('xmlns',NS);clone.setAttribute('width','1448');clone.setAttribute('height','1086');return new XMLSerializer().serializeToString(clone);}
document.querySelector('#export-svg').onclick=()=>download(new Blob([cleanSVG()],{type:'image/svg+xml;charset=utf-8'}),'gcdl-architecture.svg');
document.querySelector('#export-html').onclick=()=>{const clone=document.documentElement.cloneNode(true);clone.querySelector('#diagram').innerHTML=document.querySelector('#svg-initial').textContent;clone.querySelector('#saved-state').textContent=JSON.stringify(snapshot()).replaceAll('<','\\u003c');clone.querySelector('#saved-state').dataset.revision=Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,9);clone.querySelector('body').classList.remove('editing','clean');clone.querySelector('#edit').removeAttribute('checked');download(new Blob(['<!doctype html>\n'+clone.outerHTML],{type:'text/html;charset=utf-8'}),'gcdl-architecture.html');};
document.querySelector('#export-png').onclick=()=>{const source=URL.createObjectURL(new Blob([cleanSVG()],{type:'image/svg+xml'})),im=new Image();im.onload=()=>{const canvas=document.createElement('canvas');canvas.width=2896;canvas.height=2172;const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(im,0,0,canvas.width,canvas.height);canvas.toBlob(blob=>download(blob,'gcdl-architecture-2x.png'));URL.revokeObjectURL(source);};im.onerror=()=>{tell('导出图片失败，请改用 SVG');URL.revokeObjectURL(source);};im.src=source;};
const initialSaved=document.querySelector('#saved-state').textContent.trim();
try{let v;try{v=JSON.parse(localStorage.getItem(storeKey)||'null');}catch{}if(!validState(v))v=JSON.parse(initialSaved||'null');if(validState(v))restore(v);}catch{}
clearSelection();undoButton.disabled=true;
tell(initialSaved?'已载入保存的图形 · 1448 × 1086':'按原图布局查看 · 1448 × 1086');
fit();window.addEventListener('resize',()=>{if(!document.body.classList.contains('editing'))fit();});
window.diagramInfo={nodes:()=>nodes.size,edges:()=>edges.size,viewBox:'0 0 1448 1086'};
