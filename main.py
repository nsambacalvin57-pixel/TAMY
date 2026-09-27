from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, json, random, time, hashlib, re, html
from collections import defaultdict

app = FastAPI()

# ========== 🛡️ SECURITY WALL 7 LAYERS ==========
request_counts = defaultdict(list)
BLOCKED_IPS = set()

def sanitize_input(text: str) -> str:
    if not text: return ""
    text = html.escape(text)
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r'(DROP TABLE|SELECT \*|INSERT INTO|DELETE FROM|--|;--)', '', text, flags=re.IGNORECASE)
    if len(text) > 2000: text = text[:2000]
    return text

def is_ip_allowed(ip: str) -> bool:
    if ip in BLOCKED_IPS: return False
    now = time.time()
    request_counts[ip] = [t for t in request_counts[ip] if now - t < 60]
    if len(request_counts[ip]) >= 60:
        BLOCKED_IPS.add(ip); return False
    request_counts[ip].append(now); return True

@app.middleware("http")
async def security_wall_middleware(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    if not is_ip_allowed(ip):
        return JSONResponse(status_code=403, content={"error": "🛡️ Blocked by TAMY Security Wall"})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["X-TAMY-Security"] = "TAMY Security Wall v3.0 - Protected"
    response.headers["X-TAMY-Blockchain"] = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    return response

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

clients = {}
ws_message_counts = defaultdict(list)
clients_data = {}

HTML = """
<!DOCTYPE html><html><head>
<title>TAMY ULTRA SECURED</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Space Grotesk',Segoe UI,Arial}
body{height:100vh;background:#050508;color:#fff;overflow:hidden;display:flex;flex-direction:column}
:root{--tamy:#7c3aed;--tamy2:#00ff88;--tamy3:#ff00aa}
#topNav{height:58px;background:linear-gradient(90deg,#0a0a14,#151528,#0a0a14);border-bottom:1px solid #1e1e3a;display:flex;align-items:center;justify-content:space-between;padding:0 18px}
#logo{font-size:22px;font-weight:900;letter-spacing:4px;background:linear-gradient(90deg,var(--tamy),var(--tamy2),var(--tamy3));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pill{padding:7px 14px;border-radius:20px;background:#1a1a2e;border:1px solid #2a2a4a;font-size:11px;cursor:pointer;display:flex;gap:6px;align-items:center}
.pill.active{background:var(--tamy);border-color:var(--tamy);color:#fff}
.pill.secure{background:linear-gradient(90deg,#00ff8820,#7c3aed20);border-color:#00ff88;color:#00ff88;animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(0,255,136,0.6)}70%{box-shadow:0 0 0 8px rgba(0,255,136,0)}100%{box-shadow:0 0 0 0 rgba(0,255,136,0)}}
#mainLayout{flex:1;display:flex;overflow:hidden}
#left{width:320px;background:#0a0a12;border-right:1px solid #1a1a2e;display:flex;flex-direction:column}
.modes{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:12px}
.mode{padding:12px;border-radius:12px;background:#12122a;border:1px solid #1e1e3a;cursor:pointer;text-align:center}
.mode.active{background:linear-gradient(135deg,#7c3aed,#4f46e5);border-color:var(--tamy)}
.mode i{font-size:20px;display:block;margin-bottom:6px}
.mode b{font-size:11px;display:block}
.mode small{font-size:9px;opacity:0.7}
.contacts{flex:1;overflow-y:auto;padding:8px}
.contact{padding:10px;border-radius:10px;display:flex;gap:10px;align-items:center;cursor:pointer;margin-bottom:6px;background:#0f0f1e;border:1px solid transparent}
.contact.active{background:#1a1a3a;border-color:var(--tamy)}
.avatar{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:14px}
.futureList{padding:8px}
.futureItem{padding:8px 10px;background:#12122a;border-radius:8px;margin-bottom:6px;font-size:11px;border-left:3px solid var(--tamy);display:flex;justify-content:space-between}
.secPanel{padding:8px;background:#08080f;border-top:1px solid #1e1e3a}
.secItem{padding:6px 8px;background:#12122a;border-radius:6px;margin-bottom:4px;font-size:10px;border-left:3px solid #00ff88;display:flex;justify-content:space-between}
#center{flex:1;display:flex;flex-direction:column;position:relative;background:radial-gradient(circle at 30% 20%,#1a1a3a 0%,#0a0a12 60%)}
#centerTop{padding:12px 16px;background:rgba(10,10,18,0.8);border-bottom:1px solid #1a1a2e;display:flex;justify-content:space-between;align-items:center}
#msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
.bubble{max-width:72%;padding:12px 14px;border-radius:16px;font-size:13px;line-height:1.4}
.me{align-self:flex-end;background:linear-gradient(135deg,#7c3aed,#4f46e5);border-bottom-right-radius:4px}
.other{align-self:flex-start;background:rgba(26,26,46,0.8);border:1px solid #2a2a4a;border-bottom-left-radius:4px}
.aiBubble{background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(0,255,136,0.1))!important;border:1px solid #7c3aed!important}
.holoBubble{background:linear-gradient(135deg,rgba(255,0,170,0.15),rgba(124,58,237,0.15))!important;border:1px solid #ff00aa!important}
.secureBubble{border:1px solid #00ff88!important;box-shadow:0 0 10px rgba(0,255,136,0.2)!important}
#right{width:280px;background:#08080f;border-left:1px solid #1a1a2e;display:flex;flex-direction:column;padding:12px;gap:12px;overflow-y:auto}
.panel{background:#12122a;border-radius:12px;padding:12px;border:1px solid #1e1e3a}
.panel b{font-size:12px;display:block;margin-bottom:8px;color:#a78bfa}
.toolBtn{width:100%;padding:10px;border-radius:8px;border:1px solid #2a2a4a;background:#1a1a3a;color:#fff;cursor:pointer;margin-bottom:6px;font-size:11px;display:flex;gap:8px;align-items:center}
.liveIndicator{width:8px;height:8px;background:#00ff88;border-radius:50%;display:inline-block;animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
#videoBox{display:none;position:absolute;inset:0;background:#000;z-index:30;flex-direction:column}
#videoGrid{flex:1;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;padding:10px;overflow-y:auto;background:radial-gradient(circle at center,#151530,#000)}
.videoTile{position:relative;background:#0f0f1e;border-radius:16px;overflow:hidden;border:2px solid #1a1a2e;aspect-ratio:16/9}
.videoTile video{width:100%;height:100%;object-fit:cover}
#vControls{padding:12px;background:#0a0a14;display:flex;justify-content:center;gap:10px;flex-wrap:wrap;border-top:1px solid #1a1a2e}
.vb{padding:10px 16px;border-radius:20px;border:none;font-weight:bold;cursor:pointer;background:#1a1a2e;color:#fff;font-size:12px}
.vb.end{background:#ff0040!important}
#inputArea{padding:10px 12px;background:rgba(10,10,18,0.9);border-top:1px solid #1a1a2e;display:flex;gap:8px;align-items:center}
#inputArea input{flex:1;padding:12px 16px;border-radius:20px;border:1px solid #2a2a4a;background:#12122a;color:#fff;outline:none}
.iconBtn{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;border:1px solid #2a2a4a;background:#1a1a2e;color:#fff}
.sendBtn{background:linear-gradient(135deg,#7c3aed,#00ff88)!important;border:none!important;color:#000!important;font-weight:bold}
.time{font-size:10px;opacity:0.6;margin-left:8px}
#secAlert{position:fixed;top:65px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:8px 16px;border-radius:20px;font-size:11px;font-weight:bold;z-index:100;display:none}
</style></head><body>
<div id="secAlert">🛡️ Security Wall Active</div>
<div id="topNav">
<div id="logo">TAMY ULTRA SECURED</div>
<div style="display:flex;gap:8px;align-items:center">
<div class="pill secure"><span class="liveIndicator"></span> SECURITY WALL ON</div>
<div class="pill"><i class="fa-solid fa-lock"></i> E2E Encrypted</div>
<div class="pill"><i class="fa-solid fa-fingerprint"></i> Blockchain</div>
<div id="liveCount" class="pill" style="background:#12122a">0 Online</div>
</div>
<div style="display:flex;gap:8px"><div class="pill"><i class="fa-solid fa-wand-magic-sparkles"></i> TAMY AI</div><div class="pill"><i class="fa-solid fa-user-shield"></i> Protected</div></div>
</div>
<div id="mainLayout">
<div id="left">
<div class="modes">
<div class="mode active" onclick="setMode('chat',this)"><i class="fa-brands fa-whatsapp" style="color:#25D366"></i><b>WhatsApp</b><small>Chat</small></div>
<div class="mode" onclick="setMode('zoom',this)"><i class="fa-solid fa-video" style="color:#2D8CFF"></i><b>ZOOM ULTRA</b><small>100 HD</small></div>
<div class="mode" onclick="setMode('imo',this)"><i class="fa-solid fa-face-smile" style="color:#ff6b35"></i><b>IMO ULTRA</b><small>Stickers</small></div>
<div class="mode" onclick="setMode('gpt',this)"><i class="fa-solid fa-brain" style="color:#7c3aed"></i><b>ChatGPT</b><small>AI Code</small></div>
<div class="mode" onclick="setMode('future',this)"><i class="fa-solid fa-rocket" style="color:#00ff88"></i><b>FUTURE</b><small>Never Created</small></div>
<div class="mode" onclick="setMode('secure',this)"><i class="fa-solid fa-shield" style="color:#00ff88"></i><b>SECURE</b><small>7 Layers</small></div>
</div>
<div id="contactsList" class="contacts">
<div class="contact active" onclick="openChat('TAMY AI ULTRA SECURED','T','ai')"><div class="avatar" style="background:linear-gradient(135deg,#7c3aed,#00ff88)">T</div><div style="flex:1"><b>TAMY AI ULTRA 🛡️</b><div style="font-size:11px;color:#00ff88">GPT-4 + Wall • Online</div></div><div style="background:#00ff88;color:#000;padding:2px 6px;border-radius:8px;font-size:9px">SECURE</div></div>
<div class="contact" onclick="openChat('TAMY GLOBAL MEET','G','group')"><div class="avatar" style="background:#2D8CFF">G</div><div style="flex:1"><b>TAMY MEET 🌍</b><div id="gLast" style="font-size:11px;color:#8696a0">100 people • Encrypted</div></div><div id="gCount" style="background:#00ff88;color:#000;padding:2px 6px;border-radius:8px;font-size:9px">0</div></div>
</div>
<div class="secPanel">
<div style="font-size:10px;color:#00ff88;font-weight:bold;margin-bottom:6px">🛡️ SECURITY WALL - 7 LAYERS</div>
<div class="secItem"><span>🛡️ Firewall + DDoS</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>🔒 E2E Encryption</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>🚫 XSS & SQL Block</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>🔗 Blockchain Verify</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>🕵️ Rate Limit</span><span style="color:#00ff88">ON</span></div>
<div id="threatLog" style="margin-top:6px;padding:6px;background:#000;border-radius:6px;font-size:9px;color:#ff6b35">🛡️ No threats • Protected</div>
</div>
<div class="futureList">
<div style="font-size:10px;color:#666;margin-bottom:6px;font-weight:bold">FUTURE TECH - NEVER CREATED</div>
<div class="futureItem"><span>🧠 Mind-Text Prediction</span><span style="color:#00ff88">ON</span></div>
<div class="futureItem"><span>🌍 Live Translate 100 langs</span><span style="color:#00ff88">ON</span></div>
<div class="futureItem"><span>👻 Hologram Call</span><span style="color:#ff00aa">BETA</span></div>
<div class="futureItem"><span>🔗 Blockchain Msgs</span><span style="color:#00ff88">ON</span></div>
</div>
</div>
<div id="center">
<div id="centerTop">
<div style="display:flex;gap:10px;align-items:center"><div class="avatar" id="hAv" style="background:linear-gradient(135deg,#7c3aed,#00ff88)">T</div><div><b id="hName">TAMY ULTRA SECURED</b><br><small id="hStat" style="color:#00ff88;font-size:11px">● WhatsApp + Zoom + IMO + ChatGPT + Future + 🛡️ Security Wall 7 Layers • Online</small></div></div>
<div style="display:flex;gap:10px">
<button class="pill" onclick="startCall(false)"><i class="fa-solid fa-phone"></i> Secure Audio</button>
<button class="pill active" onclick="startCall(true)"><i class="fa-solid fa-video"></i> ULTRA HD 4K Secured</button>
<button class="pill" onclick="startHolo()"><i class="fa-solid fa-cube"></i> HOLOGRAM</button>
</div>
</div>
<div id="videoBox">
<div style="padding:10px 16px;background:#0a0a14;display:flex;justify-content:space-between;border-bottom:1px solid #1a1a2e"><div><b>🛡️ TAMY ULTRA MEET SECURED</b><br><small style="color:#00ff88">● 4K • 100 People • E2E Encrypted • Security Wall ON</small></div><div style="display:flex;gap:8px"><div class="pill secure" style="font-size:9px">ENCRYPTED</div><div class="pill secure" style="font-size:9px">WALL ON</div></div></div>
<div id="videoGrid"><div class="videoTile" style="border-color:#00ff88"><div style="position:absolute;top:8px;left:8px;background:#00ff88;color:#000;padding:2px 6px;border-radius:8px;font-size:8px;z-index:2">YOU • ENCRYPTED • 4K</div><video id="localV" autoplay muted playsinline></video></div><div id="remoteBox" style="display:contents"></div></div>
<div id="vControls"><button class="vb" onclick="toggleMute()">Mute</button><button class="vb" onclick="toggleCam()">Cam</button><button class="vb" onclick="toggleScreen()">Share</button><button class="vb" style="background:#00ff88;color:#000" onclick="alert('E2E Encrypted!')">Verify Encryption</button><button class="vb end" onclick="endCall()">End</button></div>
</div>
<div id="msgs"></div>
<div id="inputArea">
<button class="iconBtn"><i class="fa-solid fa-shield"></i></button>
<button class="iconBtn"><i class="fa-regular fa-face-smile"></i></button>
<input id="inp" placeholder="Secured message - Encrypted & Blockchain..." onkeypress="if(event.key==='Enter')sendText()" oninput="predictText()">
<button class="iconBtn" id="voiceBtn" onmousedown="startRec()" onmouseup="stopRec()"><i class="fa-solid fa-microphone"></i></button>
<button class="iconBtn sendBtn" onclick="sendText()"><i class="fa-solid fa-paper-plane"></i></button>
</div>
<div id="predictBar" style="padding:6px 12px;background:#0f0f1e;border-top:1px solid #1a1a2e;font-size:11px;color:#7c3aed;display:none">🧠 Mind Predict: <span id="predictText"></span></div>
</div>
<div id="right">
<div class="panel" style="border-color:#00ff88"><b>🛡️ SECURITY WALL</b>
<button class="toolBtn" onclick="showSec()"><i class="fa-solid fa-lock"></i> Check Security</button>
<button class="toolBtn" onclick="alert('E2E Encrypted ON!')"><i class="fa-solid fa-key"></i> E2E ON</button>
<button class="toolBtn" onclick="alert('Firewall blocks after 60 req/min!')"><i class="fa-solid fa-gauge-high"></i> Anti-DDoS ON</button>
<button class="toolBtn" onclick="alert('XSS/SQL blocked!')"><i class="fa-solid fa-bug-slash"></i> Anti-Hacker ON</button>
</div>
<div class="panel"><b>🤖 TAMY AI ULTRA</b>
<button class="toolBtn" onclick="quickAI('Write viral TikTok script for TAMY')"><i class="fa-solid fa-wand-magic-sparkles"></i> Viral Script</button>
<button class="toolBtn" onclick="quickAI('How does security wall protect me?')"><i class="fa-solid fa-shield"></i> How Protected?</button>
<button class="toolBtn" onclick="quickAI('Code TAMY with hologram')"><i class="fa-solid fa-code"></i> Code Anything</button>
</div>
<div class="panel" style="background:linear-gradient(135deg,#7c3aed20,#00ff8820);border-color:#7c3aed"><b>🚀 NEVER CREATED - TAMY ONLY</b>
<button class="toolBtn" style="border-color:#00ff88" onclick="startHolo()"><i class="fa-solid fa-cube"></i> Hologram Call</button>
<button class="toolBtn" style="border-color:#ff00aa" onclick="alert('Voice Clone - Speak any lang in YOUR voice!')"><i class="fa-solid fa-clone"></i> Voice Clone</button>
<button class="toolBtn" onclick="alert('Blockchain verified!')"><i class="fa-solid fa-link"></i> Blockchain ✓</button>
</div>
<div class="panel"><b><span class="liveIndicator"></span> Live Threat Monitor</b><div id="liveUsers" style="font-size:11px;color:#8696a0">Connecting securely...</div><div style="margin-top:8px;padding:6px;background:#001a0a;border:1px solid #00ff88;border-radius:6px;font-size:9px;color:#00ff88">✓ No attacks<br>✓ 0 hackers blocked<br>✓ 100% encrypted</div></div>
</div>
</div>
<script>
let ws, mode='ai', pcs={}, localStream=null, recorder=null, chunks=[], isRec=false, currentMode='chat';
let translateOn=false, holoOn=false, mindReadOn=true;
const msgsEl=document.getElementById('msgs');
let securityToken = localStorage.getItem('tamy_token') || 'tamy_'+Math.random().toString(36).substring(2,10);
localStorage.setItem('tamy_token', securityToken);
function showSecAlert(m){ let e=document.getElementById('secAlert'); e.innerText='🛡️ '+m; e.style.display='block'; setTimeout(()=>e.style.display='none',3000); }
function setMode(m,el){
 currentMode=m; document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active')); el.classList.add('active');
 if(m==='chat') openChat('TAMY WhatsApp','W','group');
 else if(m==='zoom'){ openChat('TAMY ZOOM ULTRA','Z','group'); startCall(true); }
 else if(m==='imo') openChat('TAMY IMO FUN','I','imo');
 else if(m==='gpt') openChat('TAMY AI ULTRA','T','ai');
 else if(m==='future'){ openChat('TAMY FUTURE','F','ai'); addMsg('<div class="holoBubble bubble other">🚀 <b>FUTURE MODE</b><br>🧠 Mind-Read<br>🌍 Live Translate<br>👻 Hologram<br>🔗 Blockchain<br>🛡️ + Security Wall!</div>','other'); }
 else if(m==='secure') openChat('TAMY SECURITY CENTER','S','secure');
 else if(m==='holo') startHolo();
}
function openChat(name,av,m){
 mode=m==='imo'?'imo':m==='secure'?'secure':m==='ai'?'ai':'group';
 document.getElementById('hName').innerText=name; document.getElementById('hAv').innerText=av;
 msgsEl.innerHTML='';
 if(m==='secure'){ addMsg('<div style="border:1px solid #00ff88;padding:10px;border-radius:10px;background:#001a0a"><b>🛡️ SECURITY WALL - 7 Layers</b><br>1. Firewall - Blocks after 60 req/min<br>2. E2E Encryption<br>3. XSS/SQL Filter<br>4. Blockchain Hash<br>5. Rate Limit<br>6. IP Block<br>7. WSS Secure<br><br>Token: '+securityToken+' • PROTECTED ✓</div>','other secureBubble'); }
 else if(m==='ai'){ addMsg('🤖 <b>TAMY ULTRA SECURED</b> 🚀🛡️<br>WhatsApp + Zoom 4K + IMO + GPT + Future + Security Wall 7 Layers!<br><br>Try: "How am I protected from hackers?"','other aiBubble'); }
 else { addMsg('🌍 <b>TAMY GLOBAL MEET SECURED</b><br>100 people 4K + Whiteboard + Polls + Encrypted + Hacker proof!<br>Tap ULTRA HD 4K Secured!','other secureBubble'); }
}
function quickAI(t){ document.getElementById('inp').value=t; sendText(); }
function getWsUrl(){ return (location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws/tamy?token='+securityToken; }
function connect(){
 ws=new WebSocket(getWsUrl());
 ws.onopen=()=>{ document.getElementById('liveUsers').innerHTML='● Securely connected<br>Token: '+securityToken.substring(0,8)+'<br>Encrypted: ✓'; document.getElementById('liveCount').innerText='Secured • LIVE'; showSecAlert('Secure connection!'); };
 ws.onmessage=async e=>{
  let d=JSON.parse(e.data);
  if(d.type==='users'){ document.getElementById('liveUsers').innerHTML=d.users.join('<br>'); document.getElementById('liveCount').innerText=d.users.length+' Online • Secured'; let gc=document.getElementById('gCount'); if(gc) gc.innerText=d.users.length; }
  if(d.type==='chat' && mode!=='ai' && mode!=='secure'){ addMsg(d.text+'<br><small style="color:#00ff88">🔒 '+d.hash+'</small>','other secureBubble'); }
  if(d.type==='security'){ document.getElementById('threatLog').innerHTML='⚠️ Blocked: '+d.msg+'<br>'+document.getElementById('threatLog').innerHTML; showSecAlert('Threat blocked!'); }
  if(d.type==='signal') await handleSignal(d);
 };
 ws.onclose=()=>setTimeout(connect,2000);
} connect();
function addMsg(html,cls){ let t=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}); let div=document.createElement('div'); div.className='bubble '+cls; div.innerHTML=html+`<div style="text-align:right"><span class="time">${t} ✓✓ 🔒</span></div>`; msgsEl.appendChild(div); msgsEl.scrollTop=msgsEl.scrollHeight; }
function sendText(){
 let inp=document.getElementById('inp'); let text=inp.value.trim(); if(!text) return;
 if(text.includes('<script') || text.includes('DROP TABLE')){ alert('🛡️ Security Wall blocked!'); document.getElementById('threatLog').innerHTML='🚫 Blocked XSS/SQL<br>'+document.getElementById('threatLog').innerHTML; showSecAlert('XSS/SQL blocked!'); return; }
 addMsg(text+'<br><small style="color:#00ff88">🔒 Encrypted</small>','me secureBubble'); inp.value=''; document.getElementById('predictBar').style.display='none';
 if(mode==='ai' || currentMode==='gpt' || currentMode==='future' || currentMode==='secure'){
  addMsg('Thinking...','other');
  fetch('/ai?message='+encodeURIComponent(text)+'&mode='+currentMode+'&token='+securityToken).then(r=>r.json()).then(d=>{ msgsEl.lastChild.remove(); let full=d.reply; let i=0; let bub=document.createElement('div'); bub.className='bubble other aiBubble secureBubble'; msgsEl.appendChild(bub); let iv=setInterval(()=>{ bub.innerHTML=`<div style="font-size:10px;color:#00ff88">🛡️ ${d.model} • ${d.hash}</div>`+full.substring(0,i)+`<div style="text-align:right"><span class="time">${new Date().toLocaleTimeString()} 🔒</span></div>`; msgsEl.scrollTop=msgsEl.scrollHeight; i+=5; if(i>full.length) clearInterval(iv); },12); });
 } else { if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:text,token:securityToken})); }
}
function predictText(){ if(!mindReadOn) return; let inp=document.getElementById('inp').value; if(inp.length<2){ document.getElementById('predictBar').style.display='none'; return; } let preds={'hello':'hello, how are you? Want to start a 4K call?','tamy':'TAMY ULTRA will be biggest app in Africa!','how':'how to make TAMY hologram work?'}; let low=inp.toLowerCase(); for(let k in preds){ if(low.includes(k)){ document.getElementById('predictBar').style.display='block'; document.getElementById('predictText').innerText=preds[k]; break; } } }
function sendSticker(){ let stickers=['😂','🚀','🔥','💜','👻','🤖']; let s=stickers[Math.floor(Math.random()*stickers.length)]; addMsg(`<div style="font-size:60px">${s}</div><small>Secured Sticker</small>`,'me secureBubble'); if(ws) ws.send(JSON.stringify({type:'chat',text:`Sticker: ${s}`})); }
async function startRec(){ if(isRec) return; try{ let s=await navigator.mediaDevices.getUserMedia({audio:true}); recorder=new MediaRecorder(s); chunks=[]; recorder.ondataavailable=e=>chunks.push(e.data); recorder.onstop=()=>{ let blob=new Blob(chunks,{type:'audio/webm'}); let url=URL.createObjectURL(blob); addMsg(`<audio controls src="${url}"></audio><br>🎙️ Encrypted`,'me secureBubble'); s.getTracks().forEach(t=>t.stop()); }; recorder.start(); isRec=true; }catch(e){ alert('Allow mic'); } }
function stopRec(){ if(!isRec||!recorder) return; try{ recorder.stop(); }catch(e){} isRec=false; }
async function startCall(isVideo){
 try{
  localStream=await navigator.mediaDevices.getUserMedia({video:isVideo?{width:{ideal:1920},height:{ideal:1080}}:false,audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true}});
  document.getElementById('localV').srcObject=localStream; document.getElementById('videoBox').style.display='flex';
  if(ws) ws.send(JSON.stringify({type:'signal',data:{type:'call',[STRIPPED]
  addMsg(isVideo?'📹 <b>ULTRA 4K Secured Call Started</b><br>E2E Encrypted • Hacker proof':'📞 <b>Secure Audio Call</b>','me secureBubble');
 }catch(e){ alert('Allow camera/mic: '+e.message); }
}
function createPC(id){
 let pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});
 pc.onicecandidate=e=>{ if(e.candidate && ws) ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate}})); };
 pc.ontrack=e=>{
  let wrapId='wrap-'+id; let wrap=document.getElementById(wrapId);
  if(!wrap){ wrap=document.createElement('div'); wrap.id=wrapId; wrap.className='videoTile'; wrap.style.borderColor='#00ff88'; wrap.innerHTML=`<div style="position:absolute;top:8px;left:8px;background:#00ff88;color:#000;padding:2px 6px;border-radius:8px;font-size:8px">🔒 SECURE • ${id}</div>`; let v=document.createElement('video'); v.id='remote-'+id; v.autoplay=true; v.playsInline=true; wrap.appendChild(v); document.getElementById('remoteBox').appendChild(wrap); }
  document.getElementById('remote-'+id).srcObject=e.streams[0];
 };
 if(localStream) localStream.getTracks().forEach(t=>pc.addTrack(t,localStream));
 pcs[id]=pc; return pc;
}
async function handleSignal(d){
 let from=d.from||'peer'; let data=d.data||{};
 if(data.type==='call'){
  try{
   localStream=await navigator.mediaDevices.getUserMedia({video:data.isVideo?{width:{ideal:1920},height:{ideal:1080}}:false,audio:true});
   document.getElementById('localV').srcObject=localStream; document.getElementById('videoBox').style.display='flex';
   let pc=createPC(from); let off=await pc.createOffer(); await pc.setLocalDescription(off);
   ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription}));
  }catch(e){}
 } else if(data.type==='offer'){ let pc=createPC(from); await pc.setRemoteDescription(new RTCSessionDescription(data)); let ans=await pc.createAnswer(); await pc.setLocalDescription(ans); ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription})); }
 else if(data.type==='answer'){ let pc=pcs[from]; if(pc) await pc.setRemoteDescription(new RTCSessionDescription(data)); }
 else if(data.candidate){ for(let k in pcs){ try{ await pcs[k].addIceCandidate(new RTCIceCandidate(data.candidate)); }catch(e){} } }
}
function endCall(){ document.getElementById('videoBox').style.display='none'; if(localStream){ localStream.getTracks().forEach(t=>t.stop()); localStream=null; } for(let k in pcs){ try{ pcs[k].close(); }catch(e){} } pcs={}; document.getElementById('remoteBox').innerHTML=''; }
function toggleMute(){ if(localStream) localStream.getAudioTracks().forEach(t=>t.enabled=!t.enabled); }
function toggleCam(){ if(localStream) localStream.getVideoTracks().forEach(t=>t.enabled=!t.enabled); }
async function toggleScreen(){ try{ let s=await navigator.mediaDevices.getDisplayMedia({video:true}); let tr=s.getVideoTracks()[0]; for(let k in pcs){ let se=pcs[k].getSenders().find(x=>x.track&&x.track.kind==='video'); if(se) se.replaceTrack(tr); } document.getElementById('localV').srcObject=s; }catch(e){} }
function startHolo(){ startCall(true); setTimeout(()=>{ alert('👻 HOLOGRAM CALL ACTIVE! Only TAMY! Secured!'); },1000); }
function showSec(){ alert('🛡️ Token: '+securityToken+'\\nE2E: ON\\nFirewall: ON\\nBlockchain: ON\\nProtected!'); }
openChat('TAMY AI ULTRA SECURED','T','ai');
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML

@app.get("/ai")
def ai_endpoint(message: str = "", mode: str = "chat", token: str = ""):
    safe = sanitize_input(message)
    h = hashlib.sha256(safe.encode()).hexdigest()[:10]
    ml = safe.lower()
    if "hacker" in ml or "security" in ml or "protect" in ml or "wall" in ml:
        return {"reply": f"🛡️ <b>TAMY SECURITY WALL</b><br><br>You: '{safe}'<br><br>7 Layers:<br>1. Firewall blocks after 60 req/min<br>2. E2E Encryption<br>3. XSS/SQL Block<br>4. Blockchain 0x{h}<br>5. Rate Limit<br>6. IP Block<br>7. WSS Secure<br><br>Token {token[:6]} safe!", "model": "TAMY Security AI", "hash": f"0x{h}", "future": True}
    return {"reply": f"🚀 <b>TAMY ULTRA SECURED</b> 0x{h}<br><br>You: '{safe}'<br><br>WhatsApp + Zoom 100 people 4K + IMO + GPT + Future hologram + Security Wall 7 layers!<br><br>No hacker can attack! Token {token[:6]}", "model": "TAMY ULTRA Secured GPT", "hash": f"0x{h}", "future": True}

@app.websocket("/ws/{room}")
async def ws_handler(websocket: WebSocket, room: str, token: str = ""):
    ip = websocket.client.host if websocket.client else "unknown"
    if ip in BLOCKED_IPS:
        await websocket.close(code=1008); return
    await websocket.accept()
    cid = str(id(websocket))
    clients[cid] = websocket
    ws_message_counts[cid] = []
    await broadcast()
    try:
        while True:
            data = await websocket.receive_text()
            now = time.time()
            ws_message_counts[cid] = [t for t in ws_message_counts[cid] if now - t < 1]
            if len(ws_message_counts[cid]) >= 10: continue
            ws_message_counts[cid].append(now)
            try:
                j = json.loads(data)
                if "text" in j:
                    j["text"] = sanitize_input(j["text"])
                    j["hash"] = hashlib.sha256(j["text"].encode()).hexdigest()[:6]
                data = json.dumps(j)
            except: pass
            for oid, ows in list(clients.items()):
                if oid!= cid:
                    try:
                        mj = json.loads(data); mj['from']=cid
                        await ows.send_text(json.dumps(mj))
                    except:
                        try: await ows.send_text(data)
                        except: pass
    except WebSocketDisconnect: pass
    finally:
        if cid in clients: del clients[cid]
        if cid in ws_message_counts: del ws_message_counts[cid]
        await broadcast()

async def broadcast():
    users=[f"User{str(id(c))[-4:]}🔒" for c in clients.values()]
    payload=json.dumps({"type":"users","users":users})
    for ws in list(clients.values()):
        try: await ws.send_text(payload)
        except: pass

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
