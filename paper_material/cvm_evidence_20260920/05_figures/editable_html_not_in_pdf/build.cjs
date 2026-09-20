const fs=require('fs'),path=require('path');
const root=__dirname;
const initial='<style>text{font-family:"Times New Roman",Times,serif;} .node text{pointer-events:none;} .edge-path{pointer-events:none;} .edge-hit{pointer-events:stroke;} </style><rect x="0" y="0" width="1448" height="1086" fill="#FFFFFF"/>';
const scripts=['core.js','panel_g.js','panel_fb.js','editor.js'].map(n=>fs.readFileSync(path.join(root,n),'utf8')).join('\n');
const html=fs.readFileSync(path.join(root,'page_template.html'),'utf8').replaceAll('__SVG_INITIAL__',initial).replace('__JS__',()=>scripts);
fs.writeFileSync(path.join(root,'architecture.html'),html);
const preview=path.resolve(root,'../cvm_architecture_html_20260918/architecture-1to1.html');
fs.writeFileSync(preview,html);
console.log(JSON.stringify({html:path.join(root,'architecture.html'),bytes:Buffer.byteLength(html),preview:'http://127.0.0.1:8768/architecture-1to1.html'}));
