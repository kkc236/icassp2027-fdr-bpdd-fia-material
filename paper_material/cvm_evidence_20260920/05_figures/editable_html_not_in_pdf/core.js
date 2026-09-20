const NS='http://www.w3.org/2000/svg';
const c={ink:'#28323C',g:'#566D83',gf:'#EDF1F5',f:'#54756E',ff:'#E8F0ED',b:'#846B54',bf:'#F1ECE5',neutral:'#F5F6F7',border:'#B6BEC5'};
const el=(tag,attrs={},parent)=>{const n=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))if(v!==undefined&&v!==null)n.setAttribute(k,v);if(parent)parent.append(n);return n;};
const svg=document.querySelector('#diagram');
const defs=el('defs',{},svg);
for(const [key,color]of Object.entries({ink:c.ink,f:c.f,g:c.g,b:c.b})){
 const marker=el('marker',{id:'arrow-'+key,viewBox:'0 0 10 10',refX:9.2,refY:5,markerWidth:6,markerHeight:6,orient:'auto',markerUnits:'strokeWidth'},defs);
 el('path',{d:'M0 0 L10 5 L0 10 Z',fill:color},marker);
}
const frameLayer=el('g',{id:'frames'},svg),edgeLayer=el('g',{id:'connections'},svg),nodeLayer=el('g',{id:'modules'},svg),labelLayer=el('g',{id:'annotations'},svg),handleLayer=el('g',{id:'handles','data-editor':'true'},svg);
const nodes=new Map(),edges=new Map();
function markerFor(stroke){return stroke===c.f?'f':stroke===c.g?'g':(stroke===c.b||stroke==='#8C725B')?'b':'ink';}
function textAt(parent,x,y,lines,opts={}){
 const size=opts.size||20,lh=opts.lineHeight||size*1.08,a=Array.isArray(lines)?lines:[lines];
 const g=el('g',{'class':opts.cls||undefined,id:opts.id||undefined},parent);
 a.forEach((line,i)=>{
  const t=el('text',{x,y:y+(i-(a.length-1)/2)*lh,'font-size':size,'fill':opts.fill||c.ink,'text-anchor':opts.anchor||'start','font-weight':opts.bold?'700':'400','font-style':opts.italic?'italic':'normal'},g);
  t.innerHTML=line;
  if(opts.textWidth&&t.getComputedTextLength()>opts.textWidth){t.setAttribute('textLength',opts.textWidth);t.setAttribute('lengthAdjust','spacingAndGlyphs');}
  if(opts.halo){t.setAttribute('paint-order','stroke');t.setAttribute('stroke','#fff');t.setAttribute('stroke-width','5');t.setAttribute('stroke-linejoin','round');}
 });return g;
}
const d={c,
 rect(id,x,y,w,h,fill,stroke,rx=0,extra={}){return el('rect',{id,x,y,width:w,height:h,rx,fill:fill||'none',stroke:stroke||'none','stroke-width':1.7,...extra},frameLayer);},
 text(x,y,lines,opts={}){return textAt(labelLayer,x,y,lines,opts);},
 node(id,x,y,w,h,lines,opts={}){
  if(nodes.has(id))throw Error('Duplicate node '+id);
  const g=el('g',{id,'class':'node','data-node':id,tabindex:'0',role:'button','aria-label':(Array.isArray(lines)?lines.join(' '):lines).replace(/<[^>]+>/g,'')},nodeLayer);
  const attrs={fill:opts.fill||c.neutral,stroke:opts.stroke||c.ink,'stroke-width':opts.strokeWidth||1.7};
  let shape;
  if(opts.shape==='ellipse'||opts.shape==='circle')shape=el('ellipse',{cx:x+w/2,cy:y+h/2,rx:w/2,ry:h/2,...attrs},g);
  else if(opts.shape==='trapezoid')shape=el('polygon',{points:`${x},${y} ${x+w},${y} ${x+w-13},${y+h} ${x+13},${y+h}`,...attrs},g);
  else shape=el('rect',{x,y,width:w,height:h,rx:opts.rx??3,...attrs},g);
  const fs=opts.fontSize||19;
  if(lines!=='')textAt(g,x+w/2,y+h/2+fs*.34+(opts.textDy||0),lines,{size:fs,anchor:'middle',bold:opts.bold,fill:opts.textFill||c.ink,lineHeight:opts.lineHeight,textWidth:opts.textWidth});
  nodes.set(id,{id,x,y,w,h,dx:0,dy:0,element:g,shape});return g;
 },
 edge(id,points,opts={}){
  if(edges.has(id))throw Error('Duplicate edge '+id);
  const stroke=opts.stroke||c.ink,g=el('g',{id,'class':'edge','data-edge':id,tabindex:'0',role:'button','aria-label':id.replaceAll('_',' ')},edgeLayer);
  const path=el('path',{'class':'edge-path',fill:'none',stroke,'stroke-width':opts.width||1.9,'stroke-linejoin':'miter','stroke-linecap':'butt','stroke-dasharray':opts.dash?'5 3':undefined,'marker-end':opts.arrow===false?undefined:`url(#arrow-${markerFor(stroke)})`},g);
  const hit=el('path',{'class':'edge-hit',fill:'none',stroke:'transparent','stroke-width':14},g);
  const e={id,points:points.map(p=>[...p]),initial:points.map(p=>[...p]),opts,element:g,path,hit};edges.set(id,e);renderEdge(e);return g;
 },
 path(id,pathD,opts={}){return el('path',{id,d:pathD,fill:opts.fill||'none',stroke:opts.stroke||c.ink,'stroke-width':opts.width||1.7},labelLayer);}
};
function renderEdge(e){const path=e.points.map((p,i)=>(i?'L':'M')+p.map(v=>Math.round(v*100)/100).join(' ')).join(' ');e.path.setAttribute('d',path);e.hit.setAttribute('d',path);}
function buildA(d){
 const {ink,g,gf,f,ff,b,bf,border,neutral}=d.c;
 d.rect('panel_a',15,19,1418,267,'#fff',border);
 d.text(25,48,'(a) Complete detector',{size:29,bold:true});
 d.rect('decoder_group',616,55,454,174,gf,g,4);
 d.text(843,83,'RT-DETR decoder (Decoder layer × 6)',{size:22,bold:true,anchor:'middle',textWidth:411});
 d.text(25,126,'Image',{size:20});
 d.node('a_backbone',83,112,115,62,'Backbone',{fontSize:21});
 d.node('a_encoder',225,95,119,96,['Hybrid','encoder'],{shape:'trapezoid',fontSize:22,fill:neutral});
 d.node('a_f',420,157,141,45,'F: P<tspan baseline-shift="sub" font-size="70%">3</tspan> refinement',{fill:ff,stroke:f,fontSize:20,bold:true,textWidth:126,textFill:f});
 d.node('a_attention',637,111,161,80,['Attention + FFN','(queries)'],{fontSize:21,textWidth:143});
 d.node('a_class',861,97,166,41,'Class head',{fontSize:21});
 d.node('a_g',862,157,165,54,['G: GCDL','localization'],{fill:gf,stroke:g,fontSize:22,bold:true,lineHeight:22});
 d.node('a_b',1179,110,117,77,['B: Local','expert'],{fill:bf,stroke:b,fontSize:23,bold:true,lineHeight:23});
 d.node('a_output',1324,116,99,69,['Classes','+ boxes'],{fontSize:23,lineHeight:22});
 d.node('a_shared',726,238,289,38,'Shared local features: P<tspan baseline-shift="sub" font-size="70%">2</tspan>, P<tspan baseline-shift="sub" font-size="70%">3</tspan><tspan baseline-shift="super" font-size="70%">*</tspan>, P<tspan baseline-shift="sub" font-size="70%">4</tspan>',{fontSize:20,stroke:f,fill:ff,textWidth:270,textFill:f});
 d.edge('a_input',[[28,143],[83,143]],{target:'a_backbone'});
 d.edge('a_backbone_encoder',[[198,143],[231.5,143]],{source:'a_backbone',target:'a_encoder'});
 d.edge('a_p5',[[343,102],[616,102]],{source:'a_encoder'});
 d.edge('a_p4',[[338,140],[616,140]],{source:'a_encoder'});
 d.edge('a_p3',[[332,181],[420,181]],{source:'a_encoder',target:'a_f'});
 d.edge('a_f_attention',[[561,181],[637,181]],{stroke:f,source:'a_f',target:'a_attention'});
 d.text(376,94,'P<tspan baseline-shift="sub" font-size="70%">5</tspan>',{size:20});
 d.text(376,132,'P<tspan baseline-shift="sub" font-size="70%">4</tspan>',{size:20});
 d.text(366,173,'P<tspan baseline-shift="sub" font-size="70%">3</tspan>',{size:20});
 d.text(575,171,'P<tspan baseline-shift="sub" font-size="70%">3</tspan><tspan baseline-shift="super" font-size="70%">*</tspan>',{size:20,fill:f});
 d.edge('a_query_class',[[798,150],[831,150],[831,117],[861,117]],{source:'a_attention',target:'a_class'});
 d.edge('a_query_g',[[798,150],[831,150],[831,183],[862,183]],{source:'a_attention',target:'a_g'});
 d.edge('a_class_bus',[[1027,117],[1062,117],[1062,138],[1145,138]],{arrow:false,source:'a_class',target:'a_joint'});
 d.edge('a_g_bus',[[1027,182],[1062,182],[1062,138],[1145,138]],{arrow:false,source:'a_g',target:'a_joint'});
 d.edge('a_final_query',[[719,191],[719,221],[1145,221],[1145,138]],{arrow:false,source:'a_attention',target:'a_joint'});
 d.edge('a_bundle_b',[[1145,138],[1179,138]],{source:'a_joint',target:'a_b'});
 d.node('a_joint',1141.5,134.5,7,7,'',{shape:'circle',fill:ink,stroke:ink});
 d.text(1129,122,'Base predictions',{size:17,anchor:'middle',textWidth:99});
 d.text(1011,229,'Final query',{size:17,anchor:'middle',halo:true});
 d.edge('a_local_b',[[1015,258],[1189,258],[1189,192]],{stroke:f,source:'a_shared',target:'a_b'});
 d.text(1265,207,'(After final layer)',{size:16,anchor:'middle',textWidth:120});
 d.edge('a_b_output',[[1296,150],[1324,150]],{source:'a_b',target:'a_output'});
}
