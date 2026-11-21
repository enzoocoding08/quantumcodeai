const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const cfg=JSON.parse(fs.readFileSync(process.argv[2]));const out=process.argv[3];const only=process.argv[4];
fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>console.log('PAGEERR',e.message));p.on('console',m=>{if(m.type()=='error')console.log('CONSOLE',m.text())});
await p.goto('file://'+__dirname+'/reel.html');await p.evaluate(c=>window.init(c),cfg);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(1200);
if(only){for(const t of only.split(',')){await p.evaluate(t=>window.setT(t),+t);await p.screenshot({path:`${out}/test_${t}.png`});}}
else{const n=Math.ceil(cfg.total*cfg.fps);for(let i=0;i<n;i++){await p.evaluate(t=>window.setT(t),i/cfg.fps);await p.screenshot({path:`${out}/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:93});if(i%150==0)console.log('frame',i,'/',n)}}
await b.close();})();
