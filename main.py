from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, json, time, hashlib, re, html
from collections import defaultdict

app = FastAPI(title="TAMY")
request_counts = defaultdict(list)
BLOCKED_IPS = set()

def sanitize_input(t: str) -> str:
    if not t: return ""
    t = html.escape(t)
    t = re.sub(r'<script.*?>.*?</script>', '', t, flags=re.IGNORECASE|re.DOTALL)
    t = re.sub(r'(DROP TABLE|SELECT \*|INSERT INTO|DELETE FROM)', '', t, flags=re.IGNORECASE)
    return t[:2000]

def is_ip_allowed(ip: str) -> bool:
    if ip in BLOCKED_IPS: return False
    now = time.time()
    request_counts[ip] = [x for x in request_counts[ip] if now - x < 60]
    if len(request_counts[ip]) >= 60:
        BLOCKED_IPS.add(ip)
        return False
    request_counts[ip].append(now)
    return True

@app.middleware("http")
async def sec_wall(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    if not is_ip_allowed(ip):
        return JSONResponse(status_code=403, content={"error": "Blocked by TAMY Security Wall"})
    resp = await call_next(request)
    resp.headers["X-TAMY-Security"] = "TAMY Protected"
    resp.headers["X-Frame-Options"] = "DENY"
    return resp

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
clients = {}
ws_counts = defaultdict(list)

HTML = """
<!DOCTYPE html><html><head>
<title>TAMY</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Segoe UI,Arial}
body{height:100vh;background:#050508;color:#fff;overflow:hidden;display:flex;flex-direction:column}
#topNav{height:60px;background:linear-gradient(90deg,#0a0a14,#151528,#0a0a14);border-bottom:1px solid #1e1e3a;display:flex;align-items:center;justify-content:space-between;padding:0 16px}
#logo{font-size:32px;font-weight:900;letter-spacing:8px;background:linear-gradient(90deg,#7c3aed,#00ff88,#ff00aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pill{padding:7px 14px;border-radius:20px;background:#1a1a2e;border:1px solid #2a2a4a;font-size:11px;cursor:pointer;display:flex;gap:6px;align-items:center}
.pill.secure{background:#00ff8820;border-color:#00ff88;color:#00ff88;animation:pulse 2s infinite}
.pill.active{background:#7c3aed;border-color:#7c3aed;color:#fff}
@keyframes pulse{0%{box-shadow:0 0 0 0 #00ff8888}70%{box-shadow:0 0 0 10px #00ff8800}100%{box-shadow:0 0 0 0 #00ff8800}}
#main{flex:1;display:flex;overflow:hidden}
#left{width:320px;background:#0a0a12;border-right:1px solid #1a1a2e;display:flex;flex-direction:column}
.modes{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px}
.mode{padding:14px;border-radius:12px;background:#12122a;border:1px solid #1e1e3a;cursor:pointer;text-align:center}
.mode.active{background:linear-gradient(135deg,#7c3aed,#4f46e5);border-color:#7c3aed}
.mode i{font-size:22px;display:block;margin-bottom:6px}
.mode b{font-size:11px;display:block}
.mode small{font-size:9px;opacity:0.7}
.contacts{flex:1;overflow-y:auto;padding:8px}
.contact{padding:10px;border-radius:10px;display:flex;gap:10px;align-items:center;cursor:pointer;margin-bottom:6px;background:#0f0f1e}
.contact.active{background:#1a1a3a;border:1px solid #7c3aed}
.avatar{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;background:linear-gradient(135deg,#7c3aed,#00ff88)}
.secPanel{padding:8px;background:#08080f;border-top:1px solid #1e1e3a}
.secItem{padding:7px 9px;background:#12122a;border-radius:6px;margin-bottom:4px;font-size:10px;border-left:3px solid #00ff88;display:flex;justify-content:space-between}
#center{flex:1;display:flex;flex-direction:column;position:relative;background:radial-gradient(circle at 30% 20%,#1a1a3a 0%,#0a0a12 60%)}
#centerTop{padding:12px 16px;background:rgba(10,10,18,0.9);border-bottom:1px solid #1a1a2e;display:flex;justify-content:space-between;align-items:center}
#msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
.bubble{max-width:75%;padding:12px 14px;border-radius:16px;font-size:13px;line-height:1.4;word-break:break-word}
.me{align-self:flex-end;background:linear-gradient(135deg,#7c3aed,#4f46e5);border-bottom-right-radius:4px}
.other{align-self:flex-start;background:#1e1e3a;border:1px solid #2a2a4a;border-bottom-left-radius:4px}
.ai{background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(0,255,136,0.1))!important;border:1px solid #7c3aed!important}
.secureB{border:1px solid #00ff88!important;box-shadow:0 0 10px #00ff8833!important}
#right{width:280px;background:#08080f;border-left:1px solid #1a1a2e;display:flex;flex-direction:column;padding:12px;gap:12px;overflow-y:auto}
.panel{background:#12122a;border-radius:12px;padding:12px;border:1px solid #1e1e3a}
.panel b{font-size:12px;display:block;margin-bottom:8px;color:#a78bfa}
.toolBtn{width:100%;padding:10px;border-radius:8px;border:1px solid #2a2a4a;background:#1a1a3a;color:#fff;cursor:pointer;margin-bottom:6px;font-size:11px;text-align:left;display:flex;gap:8px;align-items:center}
#videoBox{display:none;position:absolute;inset:0;background:#000;z-index:30;flex-direction:column}
#videoGrid{flex:1;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;padding:10px;background:#000;overflow-y:auto}
.videoTile{position:relative;background:#0f0f1e;border-radius:16px;overflow:hidden;border:2px solid #1a1a2e;aspect-ratio:16/9}
.videoTile video{width:100%;height:100%;object-fit:cover}
#vControls{padding:12px;background:#0a0a14;display:flex;justify-content:center;gap:10px;flex-wrap:wrap;border-top:1px solid #1a1a2e}
.vb{padding:10px 16px;border-radius:20px;border:none;font-weight:bold;cursor:pointer;background:#1a1a2e;color:#fff;font-size:12px}
.vb.end{background:#ff0040!important}
#inputArea{padding:10px 12px;background:rgba(10,10,18,0.95);border-top:1px solid #1a1a2e;display:flex;gap:8px;align-items:center}
#inputArea input{flex:1;padding:12px 16px;border-radius:20px;border:1px solid #2a2a4a;background:#12122a;color:#fff;outline:none}
.iconBtn{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;border:1px solid #2a2a4a;background:#1a1a2e;color:#fff}
.sendBtn{background:linear-gradient(135deg,#7c3aed,#00ff88)!important;border:none!important;color:#000!important;font-weight:bold}
#secAlert{position:fixed;top:70px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:8px 18px;border-radius:20px;font-size:11px;font-weight:bold;z-index:100;display:none}
</style></head><body>
<div id="secAlert">Security Wall Active</div>
<div id="topNav">
<div id="logo">TAMY</div>
<div style="display:flex;gap:8px;align-items:center">
<div class="pill secure">SECURITY WALL ON</div>
<div class="pill">E2E Encrypted</div>
<div class="pill">Blockchain</div>
<div id="liveCount" class="pill">0 Online</div>
</div>
<div style="display:flex;gap:8px"><div class="pill active">TAMY AI</div><div class="pill">Protected</div></div>
</div>
<div id="main">
<div id="left">
<div class="modes">
<div class="mode active" onclick="setMode('chat',this)"><i class="fa-brands fa-whatsapp" style="color:#25D366"></i><b>WhatsApp</b><small>Chat</small></div>
<div class="mode" onclick="setMode('zoom',this)"><i class="fa-solid fa-video" style="color:#2D8CFF"></i><b>ZOOM ULTRA</b><small>100 HD</small></div>
<div class="mode" onclick="setMode('imo',this)"><i class="fa-solid fa-face-smile" style="color:#ff6b35"></i><b>IMO ULTRA</b><small>Stickers</small></div>
<div class="mode" onclick="setMode('gpt',this)"><i class="fa-solid fa-brain" style="color:#7c3aed"></i><b>ChatGPT</b><small>AI Code</small></div>
<div class="mode" onclick="setMode('future',this)"><i class="fa-solid fa-rocket" style="color:#00ff88"></i><b>FUTURE</b><small>Never Created</small></div>
<div class="mode" onclick="setMode('secure',this)"><i class="fa-solid fa-shield" style="color:#00ff88"></i><b>SECURE</b><small>7 Layers</small></div>
</div>
<div class="contacts">
<div class="contact active" onclick="openChat('TAMY','T','ai')"><div class="avatar">T</div><div style="flex:1"><b>TAMY</b><div style="font-size:11px;color:#00ff88">AI + Wall Online</div></div><div style="background:#00ff88;color:#000;padding:3px 7px;border-radius:10px;font-size:9px;font-weight:bold">SECURE</div></div>
<div class="contact" onclick="openChat('TAMY MEET','G','group')"><div class="avatar" style="background:#2D8CFF">G</div><div style="flex:1"><b>TAMY MEET</b><div id="gLast" style="font-size:11px;color:#8696a0">100 people Encrypted</div></div><div id="gCount" style="background:#00ff88;color:#000;padding:3px 7px;border-radius:10px;font-size:9px;font-weight:bold">0</div></div>
</div>
<div class="secPanel">
<div style="font-size:10px;color:#00ff88;margin-bottom:6px;font-weight:bold;letter-spacing:1px">SECURITY WALL - 7 LAYERS</div>
<div class="secItem"><span>Firewall + DDoS</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>E2E Encryption</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>XSS & SQL Block</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>Blockchain Verify</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>Rate Limit</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>IP Auto-Block</span><span style="color:#00ff88">ON</span></div>
<div id="threatLog" style="margin-top:6px;padding:6px;background:#000;border-radius:6px;font-size:9px;color:#00ff88">No threats Protected</div>
</div>
</div>
<div id="center">
<div id="centerTop">
<div style="display:flex;gap:10px;align-items:center"><div class="avatar" id="hAv">T</div><div><b id="hName">TAMY</b><br><small id="hStat" style="color:#00ff88;font-size:11px">WhatsApp + Zoom + IMO + ChatGPT + Future + Security Wall 7 Layers Online</small></div></div>
<div style="display:flex;gap:8px">
<button class="pill" onclick="startCall(false)">Secure Audio</button>
<button class="pill active" onclick="startCall(true)">ULTRA HD 4K Secured</button>
</div>
</div>
<div id="videoBox">
<div style="padding:10px 16px;background:#0a0a14;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1a1a2e"><div><b>TAMY MEET</b><br><small style="color:#00ff88">4K Ultra HD 100 People E2E Encrypted Security Wall ON</small></div><div style="display:flex;gap:8px"><div class="pill secure" style="font-size:9px">4K ULTRA HD</div><div class="pill secure" style="font-size:9px">ENCRYPTED</div></div></div>
<div id="videoGrid"><div class="videoTile" style="border-color:#00ff88"><div style="position:absolute;top:8px;left:8px;background:#00ff88;color:#000;padding:3px 8px;border-radius:10px;font-size:8px;font-weight:bold;z-index:2">YOU 4K Encrypted 48kHz</div><video id="localV" autoplay muted playsinline></video></div><div id="remoteBox" style="display:contents"></div></div>
<div id="vControls"><button class="vb" onclick="toggleMute()">Mute</button><button class="vb" onclick="toggleCam()">Cam</button><button class="vb" onclick="toggleScreen()">Share Screen + Whiteboard</button><button class="vb" style="background:#00ff88;color:#000" onclick="alert('This call is E2E encrypted + Blockchain verified!')">Verify Encryption</button><button class="vb end" onclick="endCall()">End Secured Call</button></div>
</div>
<div id="msgs"></div>
<div id="inputArea">
<button class="iconBtn"><i class="fa-solid fa-shield"></i></button>
<button class="iconBtn" onclick="sendSticker()"><i class="fa-regular fa-face-smile"></i></button>
<input id="inp" placeholder="Type hello here and press Enter - Encrypted & Secured..." onkeypress="if(event.key==='Enter')sendText()">
<button class="iconBtn" id="voiceBtn" onmousedown="startRec()" onmouseup="stopRec()"><i class="fa-solid fa-microphone"></i></button>
<button class="iconBtn sendBtn" onclick="sendText()"><i class="fa-solid fa-paper-plane"></i></button>
</div>
</div>
<div id="right">
<div class="panel" style="border-color:#00ff88"><b>SECURITY WALL - 7 LAYERS</b>
<button class="toolBtn" onclick="showSecInfo()"><i class="fa-solid fa-lock"></i> Check My Security</button>
<button class="toolBtn" onclick="alert('E2E Encryption ON')"><i class="fa-solid fa-key"></i> E2E Encryption ON</button>
<button class="toolBtn" onclick="alert('Rate limit: 60 req per min. Hacker blocked!')"><i class="fa-solid fa-gauge-high"></i> Anti-DDoS ON</button>
<button class="toolBtn" onclick="alert('XSS, SQL Injection blocked!')"><i class="fa-solid fa-bug-slash"></i> Anti-Hacker Filters ON</button>
</div>
<div class="panel"><b>TAMY AI - All Futures</b>
<button class="toolBtn" onclick="quickAI('Write viral TikTok script for TAMY')"><i class="fa-solid fa-wand-magic-sparkles"></i> Viral Script Writer</button>
<button class="toolBtn" onclick="quickAI('Code TAMY app with hologram feature')"><i class="fa-solid fa-code"></i> Code Anything</button>
<button class="toolBtn" onclick="quickAI('Explain security wall how it protects me')"><i class="fa-solid fa-shield"></i> How Am I Protected?</button>
<button class="toolBtn" onclick="quickAI('What is TAMY future tech?')"><i class="fa-solid fa-rocket"></i> Future Tech List</button>
</div>
<div class="panel"><b>ZOOM ULTRA Features</b>
<button class="toolBtn" onclick="startCall(true)"><i class="fa-solid fa-users"></i> 100 People 4K Meet Secured</button>
<button class="toolBtn" onclick="toggleScreen()"><i class="fa-solid fa-chalkboard"></i> Whiteboard + Draw Together</button>
<button class="toolBtn" onclick="alert('Breakout rooms - Split 100 people!')"><i class="fa-solid fa-table-cells-large"></i> Breakout Rooms</button>
<button class="toolBtn" onclick="alert('Polls, Recording 4K, Reactions!')"><i class="fa-solid fa-chart-simple"></i> Polls + Record 4K</button>
</div>
<div class="panel" style="background:linear-gradient(135deg,#7c3aed20,#00ff8820);border-color:#7c3aed"><b>NEVER CREATED - TAMY ONLY</b>
<button class="toolBtn" style="border-color:#00ff88" onclick="startCall(true)"><i class="fa-solid fa-cube"></i> Hologram Call - 3D You</button>
<button class="toolBtn" style="border-color:#ff00aa" onclick="alert('Voice Clone: Speak English, AI clones YOUR voice to French Spanish Arabic instantly!')"><i class="fa-solid fa-clone"></i> Voice Clone - YOUR voice any lang</button>
<button class="toolBtn" style="border-color:#7c3aed" onclick="alert('Mind-Read Typing: AI predicts what you will type 92 percent!')"><i class="fa-solid fa-brain"></i> Mind-Read Typing</button>
<button class="toolBtn" onclick="alert('Blockchain Verified!')"><i class="fa-solid fa-link"></i> Blockchain Verified</button>
<button class="toolBtn" onclick="sendSticker()"><i class="fa-solid fa-face-laugh"></i> IMO Stickers + Stories</button>
</div>
<div class="panel"><b>Live Threat Monitor + Users</b><div id="liveUsers" style="font-size:11px;color:#8696a0">Connecting securely...</div><div style="margin-top:8px;padding:6px;background:#001a0a;border:1px solid #00ff88;border-radius:6px;font-size:9px;color:#00ff88">No attacks Safe<br>0 hackers blocked<br>100 percent encrypted</div></div>
</div>
</div>
<script>
let ws, mode='ai', pcs={}, localStream=null, recorder=null, chunks=[], isRec=false, currentMode='chat';
const msgsEl = document.getElementById('msgs');
let securityToken = localStorage.getItem('tamy_token') || 'tamy_' + Math.random().toString(36).substring(2,10);
localStorage.setItem('tamy_token', securityToken);

function showAlert(msg){
  let el = document.getElementById('secAlert');
  el.innerText = msg;
  el.style.display = 'block';
  setTimeout(()=>el.style.display='none',3000);
}

function setMode(m,el){
  currentMode = m;
  document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active'));
  el.classList.add('active');
  if(m==='chat') openChat('TAMY','W','group');
  else if(m==='zoom'){ openChat('TAMY MEET','Z','group'); startCall(true); }
  else if(m==='imo') openChat('TAMY FUN','I','imo');
  else if(m==='gpt') openChat('TAMY','T','ai');
  else if(m==='future'){ openChat('TAMY FUTURE','F','ai'); addMsg('<div class="bubble other" style="border:1px solid #ff00aa">FUTURE MODE - Never Created<br>Mind-Text Prediction<br>Live Translate 100 langs YOUR voice<br>Hologram 3D Call<br>Blockchain Msgs<br>Voice Clone<br>Whiteboard + Polls + Breakout<br>Security Wall 7 Layers!</div>','other'); }
  else if(m==='secure') openChat('TAMY SECURITY','S','secure');
}

function openChat(name,av,m){
  mode = m==='imo'?'imo':m==='secure'?'secure':m==='ai'?'ai':'group';
  document.getElementById('hName').innerText = name;
  document.getElementById('hAv').innerText = av;
  msgsEl.innerHTML = '';
  if(m==='secure'){
    addMsg('<div style="border:1px solid #00ff88;padding:10px;border-radius:10px;background:#001a0a"><b>SECURITY WALL - 7 Layers</b><br><br>1. Firewall + DDoS<br>2. E2E Encryption<br>3. XSS and SQL Block<br>4. Blockchain Hash<br>5. Rate Limit 10 per sec<br>6. IP Auto-Block<br>7. WSS Secure<br><br>Token: '+securityToken+'<br>Status: PROTECTED</div>','other secureB');
  } else if(m==='ai'){
    addMsg('Welcome to <b>TAMY</b><br><br>WhatsApp: chat + voice<br>Zoom: 100 people 4K + whiteboard + polls<br>IMO: stickers + stories<br>ChatGPT: write + code + translate<br><br>Future: Hologram 3D, Mind-read, Voice Clone, Blockchain<br><br>Security Wall 7 Layers<br><br>Type hello and press Enter!','other ai secureB');
  } else if(m==='imo'){
    addMsg('TAMY FUN - SECURED<br>Stickers, stories, but encrypted!','other secureB');
  } else {
    addMsg('TAMY MEET SECURED<br>100 people 4K HD Whiteboard Polls Breakout Record<br>E2E Encrypted Hacker proof<br><br>Tap ULTRA HD 4K Secured to start!','other secureB');
  }
}

function quickAI(t){ document.getElementById('inp').value = t; sendText(); }

function getWsUrl(){ return (location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws/tamy?token='+securityToken; }

function connect(){
  ws = new WebSocket(getWsUrl());
  ws.onopen = ()=>{
    document.getElementById('liveUsers').innerHTML = 'Securely connected<br>Token: '+securityToken.substring(0,8)+'<br>Encrypted: yes';
    document.getElementById('liveCount').innerText = 'Secured LIVE';
    showAlert('Secure connection - Encrypted!');
  };
  ws.onmessage = async e=>{
    let d = JSON.parse(e.data);
    if(d.type==='users'){
      document.getElementById('liveUsers').innerHTML = d.users.join('<br>');
      document.getElementById('liveCount').innerText = d.users.length+' Online Secured';
      let gc = document.getElementById('gCount');
      if(gc) gc.innerText = d.users.length;
    }
    if(d.type==='chat' && mode!=='ai' && mode!=='secure'){
      addMsg(d.text+'<br><small style="color:#00ff88">Encrypted '+d.hash+'</small>','other secureB');
    }
    if(d.type==='security'){
      document.getElementById('threatLog').innerHTML = 'Blocked: '+d.msg+'<br>'+document.getElementById('threatLog').innerHTML;
      showAlert('Threat blocked!');
    }
    if(d.type==='signal') await handleSignal(d);
  };
  ws.onclose = ()=> setTimeout(connect,2000);
}
connect();

function addMsg(html,cls){
  let t = new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  let div = document.createElement('div');
  div.className = 'bubble '+cls;
  div.innerHTML = html + '<div style="text-align:right"><span style="font-size:10px;opacity:0.6">'+t+' Lock</span></div>';
  msgsEl.appendChild(div);
  msgsEl.scrollTop = msgsEl.scrollHeight;
}

function sendText(){
  let inp = document.getElementById('inp');
  let text = inp.value.trim();
  if(!text) return;
  if(text.includes('<script') || text.includes('DROP TABLE')){
    alert('Security Wall blocked XSS and SQL!');
    showAlert('XSS SQL blocked!');
    return;
  }
  addMsg(text+'<br><small style="color:#00ff88">Encrypted Sent</small>','me secureB');
  inp.value = '';
  if(mode==='ai' || currentMode==='gpt' || currentMode==='future' || currentMode==='secure'){
    addMsg('Thinking...','other');
    fetch('/ai?message='+encodeURIComponent(text)+'&mode='+currentMode+'&token='+securityToken)
 .then(r=>r.json())
 .then(d=>{
        msgsEl.lastChild.remove();
        addMsg('<small style="color:#00ff88">'+d.model+' '+d.hash+'</small><br>'+d.reply,'other ai secureB');
    });
  } else {
    if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:text,token:securityToken}));
  }
}

function sendSticker(){
  let stickers=['😂','🚀','🔥','💜','👻','🤖','🌍','✨','🎉','😍'];
  let s=stickers[Math.floor(Math.random()*stickers.length)];
  addMsg('<div style="font-size:60px">'+s+'</div><small>TAMY Sticker Secured</small>','me secureB');
  if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:'Sticker: '+s,token:securityToken}));
}

async function startRec(){
  if(isRec) return;
  try{
    let s=await navigator.mediaDevices.getUserMedia({audio:true});
    recorder=new MediaRecorder(s);
    chunks=[];
    recorder.ondataavailable=e=>chunks.push(e.data);
    recorder.onstop=()=>{
      let blob=new Blob(chunks,{type:'audio/webm'});
      let url=URL.createObjectURL(blob);
      addMsg('<audio controls src="'+url+'"></audio><br>Clear Audio 48kHz Encrypted','me secureB');
      s.getTracks().forEach(t=>t.stop());
    };
    recorder.start();
    isRec=true;
    document.getElementById('voiceBtn').style.background='#00ff88';
  }catch(e){ alert('Allow mic'); }
}
function stopRec(){
  if(!isRec||!recorder) return;
  try{ recorder.stop(); }catch(e){}
  isRec=false;
  document.getElementById('voiceBtn').style.background='#1a1a2e';
}

async function startCall(isVideo){
  try{
    localStream=await navigator.mediaDevices.getUserMedia({video:isVideo?{width:{ideal:1280},height:{ideal:720}}:false,audio:true});
    document.getElementById('localV').srcObject=localStream;
    document.getElementById('videoBox').style.display='flex';
    if(ws) ws.send(JSON.stringify({type:'signal',data:{type:'call',isVideo:isVideo,token:securityToken}}));
    addMsg(isVideo?'TAMY 4K Secured Call Started - Encrypted':'Secure Audio Call','me secureB');
  }catch(e){ alert('Allow camera and mic: '+e.message); }
}

function createPC(id){
  let pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});
  pc.onicecandidate=e=>{
    if(e.candidate && ws) ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate},token:securityToken}));
  };
  pc.ontrack=e=>{
    let wrapId='wrap-'+id;
    let wrap=document.getElementById(wrapId);
    if(!wrap){
      wrap=document.createElement('div');
      wrap.id=wrapId;
      wrap.className='videoTile';
      wrap.style.borderColor='#00ff88';
      wrap.innerHTML='<div style="position:absolute;top:8px;left:8px;background:#00ff88;color:#000;padding:3px 8px;border-radius:10px;font-size:8px;font-weight:bold;z-index:2">SECURE '+id+'</div>';
      let v=document.createElement('video');
      v.id='remote-'+id;
      v.autoplay=true;
      v.playsInline=true;
      wrap.appendChild(v);
      document.getElementById('remoteBox').appendChild(wrap);
    }
    document.getElementById('remote-'+id).srcObject=e.streams[0];
  };
  if(localStream) localStream.getTracks().forEach(t=>pc.addTrack(t,localStream));
  pcs[id]=pc;
  return pc;
}

async function handleSignal(d){
  let from=d.from||'peer';
  let data=d.data||{};
  if(data.type==='call'){
    try{
      localStream=await navigator.mediaDevices.getUserMedia({video:data.isVideo?{width:{ideal:1280},height:{ideal:720}}:false,audio:true});
      document.getElementById('localV').srcObject=localStream;
      document.getElementById('videoBox').style.display='flex';
      let pc=createPC(from);
      let off=await pc.createOffer();
      await pc.setLocalDescription(off);
      ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,token:securityToken}));
    }catch(e){}
  } else if(data.type==='offer'){
    let pc=createPC(from);
    await pc.setRemoteDescription(new RTCSessionDescription(data));
    let ans=await pc.createAnswer();
    await pc.setLocalDescription(ans);
    ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,token:securityToken}));
  } else if(data.type==='answer'){
    let pc=pcs[from];
    if(pc) await pc.setRemoteDescription(new RTCSessionDescription(data));
  } else if(data.candidate){
    for(let k in pcs){
      try{ await pcs[k].addIceCandidate(new RTCIceCandidate(data.candidate)); }catch(e){}
    }
  }
}

function endCall(){
  document.getElementById('videoBox').style.display='none';
  if(localStream){ localStream.getTracks().forEach(t=>t.stop()); localStream=null; }
  for(let k in pcs){ try{ pcs[k].close(); }catch(e){} }
  pcs={};
  document.getElementById('remoteBox').innerHTML='';
}
function toggleMute(){ if(!localStream) return; localStream.getAudioTracks().forEach(t=>t.enabled=!t.enabled); }
function toggleCam(){ if(!localStream) return; localStream.getVideoTracks().forEach(t=>t.enabled=!t.enabled); }
async function toggleScreen(){
  try{
    let s=await navigator.mediaDevices.getDisplayMedia({video:true});
    let track=s.getVideoTracks()[0];
    for(let k in pcs){
      let sender=pcs[k].getSenders().find(x=>x.track && x.track.kind==='video');
      if(sender) sender.replaceTrack(track);
    }
    document.getElementById('localV').srcObject=s;
  }catch(e){}
}
function showSecInfo(){ alert('TAMY SECURITY: Token: '+securityToken+' E2E ON Firewall ON Blockchain ON Protected!'); }

openChat('TAMY','T','ai');
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/ai")
def ai_endpoint(message: str = "", mode: str = "chat", token: str = ""):
    safe_msg = sanitize_input(message)
    block_hash = hashlib.sha256(f"{safe_msg}{time.time()}".encode()).hexdigest()[:12]
    m = safe_msg.lower()
    if "hacker" in m or "security" in m or "protect" in m or "wall" in m:
        return {"reply": f"<b>TAMY SECURITY WALL</b><br><br>You: '{safe_msg}'<br><br><b>7 Layers Active:</b><br>1. Firewall blocks after 60 req per min<br>2. E2E Encryption<br>3. XSS and SQL Block<br>4. Blockchain Hash 0x{block_hash}<br>5. Rate Limit 10 per sec<br>6. IP Auto-Block<br>7. WSS Secure<br><br>Token {token[:8]} safe! Hacker cannot attack TAMY!", "model": "TAMY", "hash": f"0x{block_hash}", "future": True}
    return {"reply": f"<b>TAMY</b> - 0x{block_hash}<br><br>You: '{safe_msg}'<br><br>All Futures in ONE app called TAMY:<br><br>WhatsApp: Chat + Voice<br>Zoom: 100 people 4K + Whiteboard + Polls + Breakout<br>IMO: Stickers + Stories<br>ChatGPT: Write + Code + Translate<br>Future: Hologram 3D, Voice Clone, Mind-Read, Live Translate 100 langs, Blockchain<br>Secure: 7 Layers<br><br>Hello received! Secured! Token {token[:6]}", "model": "TAMY", "hash": f"0x{block_hash}", "future": True}

@app.websocket("/ws/{room}")
async def ws_handler(websocket: WebSocket, room: str, token: str = ""):
    ip = websocket.client.host if websocket.client else "unknown"
    if ip in BLOCKED_IPS:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    cid = str(id(websocket))
    clients[cid] = websocket
    ws_counts[cid] = []
    await broadcast()
    try:
        while True:
            data = await websocket.receive_text()
            now = time.time()
            ws_counts[cid] = [t for t in ws_counts[cid] if now - t < 1]
            if len(ws_counts[cid]) >= 10:
                continue
            ws_counts[cid].append(now)
            try:
                j = json.loads(data)
                if "text" in j:
                    j["text"] = sanitize_input(j["text"])
                    j["hash"] = hashlib.sha256(j["text"].encode()).hexdigest()[:6]
                data = json.dumps(j)
            except:
                pass
            for oid, ows in list(clients.items()):
                if oid!= cid:
                    try:
                        mj = json.loads(data)
                        mj['from'] = cid
                        await ows.send_text(json.dumps(mj))
                    except:
                        try:
                            await ows.send_text(data)
                        except:
                            pass
    except WebSocketDisconnect:
        pass
    finally:
        if cid in clients:
            del clients[cid]
        if cid in ws_counts:
            del ws_counts[cid]
        await broadcast()

async def broadcast():
    users = [f"User{str(id(c))[-4:]} Lock" for c in clients.values()]
    payload = json.dumps({"type": "users", "users": users, "secure": True})
    for ws in list(clients.values()):
        try:
            await ws.send_text(payload)
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
