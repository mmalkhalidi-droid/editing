const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{
 const [,,html,mode,out,...rest]=process.argv;
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('console',m=>console.log('console:',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+html);await p.waitForFunction(()=>window.READY);await p.waitForTimeout(300);
 if(mode==='stills'){for(const t of rest){await p.evaluate(t=>render(+t),t);await p.screenshot({path:`${out}/still_${t}.jpg`,type:'jpeg',quality:80});}}
 else{const total=+rest[0],fps=30,n=Math.ceil(total*fps);
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<n;i++){await p.evaluate(t=>render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:92});
   if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r)); if(i%150==0)console.log('frame',i,'/',n);}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));}
 await b.close();})();
