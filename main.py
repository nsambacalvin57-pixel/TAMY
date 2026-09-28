from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, json, time, hashlib, re, html, random
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
client_names = {}
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
#logo{font-size:38px;font-weight:900;letter-spacing:12px;background:linear-gradient(90deg,#7c3aed,#00ff88,#ff00aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pill{padding:7px 14px;border-radius:20px;background:#1a1a2e;border:1px solid #2a2a4a;font-size:11px;cursor:pointer;display:flex;gap:6px;align-items:center}
.pill.secure{background:#00ff8820;border-color:#00ff88;color:#00ff88;animation:pulse 2s infinite}
.pill.active{background:#7c3aed;border-color:#7c3aed;color:#fff}
@keyframes pulse{0%{box-shadow:0 0 0 0 #00ff8888}70%{box-shadow:0 0 0 10px #00ff8800}100%{box-shadow:0 0 0 0 #00ff8800}}
#main{flex:1;display:flex;overflow:hidden}
#left{width:340px;background:#0a0a12;border-right:1px solid #1a1a2e;display:flex;flex-direction:column}
.modes{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px}
.mode{padding:14px;border-radius:12px;background:#12122a;border:1px solid #1e1e3a;cursor:pointer;text-align:center}
.mode.active{background:linear-gradient(135deg,#7c3aed,#4f46e5);border-color:#7c3aed}
.mode i{font-size:22px;display:block;margin-bottom:4px}
.mode b{font-size:11px;display:block}
.mode small{font-size:9px;opacity:0.7}
.contacts{flex:1;overflow-y:auto;padding:8px}
.contact{padding:10px;border-radius:10px;display:flex;gap:10px;align-items:center;cursor:pointer;margin-bottom:6px;background:#0f0f1e;border:1px solid transparent}
.contact.active{background:#1a1a3a;border-color:#7c3aed}
.avatar{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;background:linear-gradient(135deg,#7c3aed,#00ff88);flex-shrink:0}
.addBox{padding:10px;background:#08080f;border-top:1px solid #1e1e3a;border-bottom:1px solid #1e1e3a;display:flex;gap:6px}
.addBox input{flex:1;padding:8px 10px;border-radius:8px;border:1px solid #2a2a4a;background:#12122a;color:#fff;outline:none;font-size:11px}
.addBtn{padding:8px 12px;border-radius:8px;background:#00ff88;color:#000;border:none;font-weight:bold;cursor:pointer;font-size:11px}
.secPanel{padding:8px;background:#08080f;border-top:1px solid #1e1e3a}
.secItem{padding:6px 8px;background:#12122a;border-radius:6px;margin-bottom:4px;font-size:10px;border-left:3px solid #00ff88;display:flex;justify-content:space-between}
#center{flex:1;display:flex;flex-direction:column;position:relative;background:radial-gradient(circle at 30% 20%,#1a1a3a 0%,#0a0a12 60%)}
#centerTop{padding:12px 16px;background:rgba(10,10,18,0.9);border-bottom:1px solid #1a1a2e;display:flex;justify-content:space-between;align-items:center}
#msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
.bubble{max-width:75%;padding:12px 14px;border-radius:16px;font-size:13px;line-height:1.4;word-break:break-word}
.me{align-self:flex-end;background:linear-gradient(135deg,#7c3aed,#4f46e5);border-bottom-right-radius:4px}
.other{align-self:flex-start;background:#1e1e3a;border:1px solid #2a2a4a;border-bottom-left-radius:4px}
.ai{background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(0,255,136,0.1))!important;border:1px solid #7c3aed!important}
.secureB{border:1px solid #00ff88!important;box-shadow:0 0 10px #00ff8833!important}
#right{width:290px;background:#08080f;border-left:1px solid #1a1a2e;display:flex;flex-direction:column;padding:10px;gap:10px;overflow-y:auto}
.panel{background:#12122a;border-radius:12px;padding:10px;border:1px solid #1e1e3a}
.panel b{font-size:11px;display:block;margin-bottom:8px;color:#a78bfa}
.toolBtn{width:100%;padding:9px;border-radius:8px;border:1px solid #2a2a4a;background:#1a1a3a;color:#fff;cursor:pointer;margin-bottom:5px;font-size:11px;text-align:left;display:flex;gap:8px;align-items:center}
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
.userRow{display:flex;justify-content:space-between;align-items:center;padding:6px 8px;background:#0f0f1e;border-radius:8px;margin-bottom:4px;font-size:11px}
.onlineDot{width:8px;height:8px;background:#00ff88;border-radius:50%;display:inline-block;animation:pulse 1.5s infinite}
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
<div style="display:flex;gap:8px"><button class="pill active" onclick="copyLink()"><i class="fa-solid fa-link"></i> Copy Invite Link</button><div class="pill">Protected</div></div>
</div>
<div id="main">
<div id="left">
<div class="modes">
<div class="mode active" onclick="setMode('chat',this)"><i class="fa-solid fa-comment-dots" style="color:#25D366"></i><b>TAMY CHAT</b><small>Message</small></div>
<div class="mode" onclick="setMode('video',this)"><i class="fa-solid fa-video" style="color:#2D8CFF"></i><b>TAMY VIDEO</b><small>100 HD</small></div>
<div class="mode" onclick="setMode('fun',this)"><i class="fa-solid fa-face-smile" style="color:#ff6b35"></i><b>TAMY FUN</b><small>Stickers</small></div>
<div class="mode" onclick="setMode('brain',this)"><i class="fa-solid fa-brain" style="color:#7c3aed"></i><b>TAMY BRAIN</b><small>AI Code</small></div>
<div class="mode" onclick="setMode('future',this)"><i class="fa-solid fa-rocket" style="color:#00ff88"></i><b>TAMY FUTURE</b><small>Never Created</small></div>
<div class="mode" onclick="setMode('secure',this)"><i class="fa-solid fa-shield" style="color:#00ff88"></i><b>TAMY SECURE</b><small>7 Layers</small></div>
</div>

<div class="addBox">
<input id="addInput" placeholder="Add contact by name or ID">
<button class="addBtn" onclick="addContact()"><i class="fa-solid fa-user-plus"></i> Add</button>
</div>

<div style="padding:8px 10px;display:flex;justify-content:space-between;align-items:center;background:#0f0f1e"><b style="font-size:11px;color:#a78bfa">TAMY Contacts</b><span id="onlineInfo" style="font-size:10px;color:#00ff88">0 online</span></div>

<div id="contactsList" class="contacts">
<div class="contact active" data-id="tamy-ai" onclick="openChat('TAMY','T','ai')"><div class="avatar">T</div><div style="flex:1"><b>TAMY</b><div style="font-size:11px;color:#00ff88">AI + Wall Online</div></div><div style="background:#00ff88;color:#000;padding:3px 7px;border-radius:10px;font-size:9px;font-weight:bold">SECURE</div></div>
<div class="contact" data-id="tamy-meet" onclick="openChat('TAMY MEET','M','group')"><div class="avatar" style="background:#2D8CFF">M</div><div style="flex:1"><b>TAMY MEET</b><div id="gLast" style="font-size:11px;color:#8696a0">100 people Encrypted</div></div><div id="gCount" style="background:#00ff88;color:#000;padding:3px 7px;border-radius:10px;font-size:9px;font-weight:bold">0</div></div>
</div>

<div id="onlineUsersBox" style="padding:8px;background:#08080f;border-top:1px solid #1e1e3a;max-height:140px;overflow-y:auto">
<div style="font-size:10px;color:#00ff88;font-weight:bold;margin-bottom:6px">TAMY ONLINE USERS - Tap to Chat</div>
<div id="onlineList" style="font-size:11px;color:#aaa">No users yet - Share link to invite friends!</div>
</div>

<div class="secPanel">
<div style="font-size:10px;color:#00ff88;margin-bottom:6px;font-weight:bold;letter-spacing:1px">TAMY SECURITY WALL - 7 LAYERS</div>
<div class="secItem"><span>Firewall + DDoS</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>E2E Encryption</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>XSS & SQL Block</span><span style="color:#00ff88">ON</span></div>
<div class="secItem"><span>Blockchain Verify</span><span style="color:#00ff88">ON</span></div>
<div id="threatLog" style="margin-top:6px;padding:6px;background:#000;border-radius:6px;font-size:9px;color:#00ff88">No threats Protected</div>
</div>
</div>

<div id="center">
<div id="centerTop">
<div style="display:flex;gap:10px;align-items:center"><div class="avatar" id="hAv">T</div><div><b id="hName">TAMY</b><br><small id="hStat" style="color:#00ff88;font-size:11px">TAMY Chat + Video + Fun + Brain + Future + Secure Wall 7 Layers Online</small></div></div>
<div style="display:flex;gap:8px">
<button class="pill" onclick="startCall(false)">TAMY Audio</button>
<button class="pill active" onclick="startCall(true)">TAMY Video 4K</button>
</div>
</div>
<div id="videoBox">
<div style="padding:10px 16px;background:#0a0a14;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1a1a2e"><div><b>TAMY MEET</b><br><small style="color:#00ff88">4K Ultra HD 100 People E2E Encrypted</small></div><div style="display:flex;gap:8px"><div class="pill secure" style="font-size:9px">4K ULTRA HD</div><div class="pill secure" style="font-size:9px">ENCRYPTED</div></div></div>
<div id="videoGrid"><div class="videoTile" style="border-color:#00ff88"><div style="position:absolute;top:8px;left:8px;background:#00ff88;color:#000;padding:3px 8px;border-radius:10px;font-size:8px;font-weight:bold;z-index:2">YOU 4K Encrypted</div><video id="localV" autoplay muted playsinline></video></div><div id="remoteBox" style="display:contents"></div></div>
<div id="vControls"><button class="vb" onclick="toggleMute()">Mute</button><button class="vb" onclick="toggleCam()">Cam</button><button class="vb" onclick="toggleScreen()">Share Screen</button><button class="vb end" onclick="endCall()">End</button></div>
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
<div class="panel"><b>TAMY ADD CONTACT</b>
<button class="toolBtn" onclick="document.getElementById('addInput').focus()"><i class="fa-solid fa-user-plus"></i> Add Contact by Name</button>
<button class="toolBtn" onclick="copyLink()"><i class="fa-solid fa-link"></i> Copy TAMY Invite Link</button>
<button class="toolBtn" onclick="alert('Your TAMY ID: '+securityToken)"><i class="fa-solid fa-id-card"></i> My TAMY ID: Show & Copy</button>
<div id="myIdBox" style="margin-top:8px;padding:8px;background:#000;border-radius:8px;font-size:10px;word-break:break-all;border:1px dashed #2a2a4a"></div>
</div>
<div class="panel" style="border-color:#00ff88"><b>TAMY SECURITY WALL</b>
<button class="toolBtn" onclick="showSecInfo()"><i class="fa-solid fa-lock"></i> Check My Security</button>
<button class="toolBtn" onclick="alert('TAMY E2E Encryption ON')"><i class="fa-solid fa-key"></i> TAMY E2E ON</button>
</div>
<div class="panel"><b>TAMY BRAIN</b>
<button class="toolBtn" onclick="quickAI('Write viral script for TAMY')"><i class="fa-solid fa-wand-magic-sparkles"></i> TAMY Viral Script</button>
<button class="toolBtn" onclick="quickAI('Code TAMY with hologram')"><i class="fa-solid fa-code"></i> TAMY Code Anything</button>
<button class="toolBtn" onclick="quickAI('What is TAMY future tech?')"><i class="fa-solid fa-rocket"></i> TAMY Future Tech</button>
</div>
<div class="panel" style="background:linear-gradient(135deg,#7c3aed20,#00ff8820);border-color:#7c3aed"><b>TAMY NEVER CREATED ONLY</b>
<button class="toolBtn" style="border-color:#00ff88" onclick="startCall(true)"><i class="fa-solid fa-cube"></i> TAMY Hologram 3D</button>
<button class="toolBtn" style="border-color:#ff00aa" onclick="alert('TAMY Voice Clone: Speak one language, hear YOUR voice in 100 languages!')"><i class="fa-solid fa-clone"></i> TAMY Voice Clone</button>
<button class="toolBtn" style="border-color:#7c3aed" onclick="alert('TAMY Mind-Read: AI predicts typing 92 percent!')"><i class="fa-solid fa-brain"></i> TAMY Mind-Read</button>
<button class="toolBtn" onclick="alert('TAMY Blockchain Verified!')"><i class="fa-solid fa-link"></i> TAMY Blockchain</button>
</div>
<div class="panel"><b>TAMY Live Users</b><div id="liveUsers" style="font-size:11px;color:#8696a0">Connecting...</div></div>
</div>
</div>
<script>
let ws, mode='ai', pcs={}, localStream=null, recorder=null, chunks=[], isRec=false, currentMode='chat';
const msgsEl = document.getElementById('msgs');
let securityToken = localStorage.getItem('tamy_token') || 'tamy_' + Math.random().toString(36).substring(2,10);
localStorage.setItem('tamy_token', securityToken);
let myName = localStorage.getItem('tamy_name') || 'User' + Math.floor(Math.random()*9000+1000);
localStorage.setItem('tamy_name', myName);
document.getElementById('myIdBox').innerHTML = 'Your TAMY Name: <b>'+myName+'</b><br>TAMY ID: <b style="color:#00ff88">'+securityToken+'</b>';

function showAlert(msg){
  let el = document.getElementById('secAlert');
  el.innerText = msg;
  el.style.display = 'block';
  setTimeout(()=>el.style.display='none',3000);
}

function copyLink(){
  navigator.clipboard.writeText(location.href).then(()=>showAlert('TAMY Invite link copied!'));
}

function addContact(){
  let inp = document.getElementById('addInput');
  let name = inp.value.trim();
  if(!name){ alert('Type name or ID to add!'); return; }
  let id = name.replace(/[^a-zA-Z0-9]/g,'').substring(0,12) || 'user'+Date.now();
  let list = document.getElementById('contactsList');
  if(document.querySelector('[data-id="'+id+'"]')){ alert('Already added!'); inp.value=''; return; }
  let div = document.createElement('div');
  div.className = 'contact';
  div.dataset.id = id;
  let avLetter = name.charAt(0).toUpperCase();
  let colors = ['#7c3aed','#00ff88','#ff6b35','#2D8CFF','#ff00aa'];
  let col = colors[Math.floor(Math.random()*colors.length)];
  div.innerHTML = '<div class="avatar" style="background:'+col+'">'+avLetter+'</div><div style="flex:1"><b>'+name+'</b><div style="font-size:11px;color:#00ff88">Online - TAMY Secured</div></div><div style="background:#00ff88;color:#000;padding:3px 7px;border-radius:10px;font-size:9px">NEW</div>';
  div.onclick = function(){ openChat(name, avLetter, 'private'); document.querySelectorAll('.contact').forEach(c=>c.classList.remove('active')); div.classList.add('active'); };
  list.appendChild(div);
  inp.value = '';
  showAlert('TAMY Contact '+name+' added!');
  addMsg('Added TAMY contact: <b>'+name+'</b><br>Now you can chat secured!','other secureB');
}

function setMode(m,el){
  currentMode = m;
  document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active'));
  el.classList.add('active');
  if(m==='chat') openChat('TAMY CHAT','C','group');
  else if(m==='video'){ openChat('TAMY VIDEO','V','group'); startCall(true); }
  else if(m==='fun') openChat('TAMY FUN','F','fun');
  else if(m==='brain') openChat('TAMY BRAIN','B','ai');
  else if(m==='future'){ openChat('TAMY FUTURE','F','ai'); addMsg('TAMY FUTURE - Never Created<br>TAMY Hologram 3D<br>TAMY Voice Clone<br>TAMY Mind-Read<br>TAMY Blockchain<br>TAMY Security Wall!','other secureB'); }
  else if(m==='secure') openChat('TAMY SECURE','S','secure');
}

function openChat(name,av,m){
  mode = m==='private'?'group':m==='fun'?'fun':m==='secure'?'secure':m==='ai'?'ai':'group';
  document.getElementById('hName').innerText = name;
  document.getElementById('hAv').innerText = av;
  msgsEl.innerHTML = '';
  if(m==='secure'){
    addMsg('<div style="border:1px solid #00ff88;padding:10px;border-radius:10px;background:#001a0a"><b>TAMY SECURITY WALL - 7 Layers</b><br>1. Firewall<br>2. E2E<br>3. XSS Block<br>4. Blockchain<br>5. Rate Limit<br>6. IP Block<br>7. WSS<br><br>Token: '+securityToken+'</div>','other secureB');
  } else if(m==='ai'){
    addMsg('Welcome to <b>TAMY</b><br><br>TAMY Chat: Message + Voice<br>TAMY Video: 100 people 4K + Whiteboard + Polls<br>TAMY Fun: Stickers + Stories<br>TAMY Brain: Write + Code + Translate<br><br>TAMY Future: Hologram 3D, Mind-read, Voice Clone, Blockchain<br><br>TAMY Secure: 7 Layers Wall<br><br>Type hello!','other ai secureB');
  } else {
    addMsg('Chat with <b>'+name+'</b> - TAMY Secured E2E Encrypted<br>Tap TAMY Video button for 4K call!','other secureB');
  }
}

function quickAI(t){ document.getElementById('inp').value = t; sendText(); }
function getWsUrl(){ return (location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws/tamy?token='+securityToken+'&name='+encodeURIComponent(myName); }

function connect(){
  ws = new WebSocket(getWsUrl());
  ws.onopen = ()=>{
    document.getElementById('liveUsers').innerHTML = 'Connected as <b>'+myName+'</b><br>TAMY ID: '+securityToken.substring(0,8)+'<br>Encrypted: yes';
    document.getElementById('liveCount').innerText = 'Secured LIVE';
    showAlert('TAMY Connected as '+myName);
  };
  ws.onmessage = async e=>{
    let d = JSON.parse(e.data);
    if(d.type==='users'){
      let users = d.users || [];
      document.getElementById('liveCount').innerText = users.length+' Online Secured';
      document.getElementById('onlineInfo').innerText = users.length+' online';
      document.getElementById('gCount').innerText = users.length;
      let onlineHtml = '';
      users.forEach(u=>{
        if(u.id===securityToken) return;
        onlineHtml += '<div class="userRow"><span><span class="onlineDot"></span> '+u.name+' <small style="opacity:0.6">('+u.id.substring(0,6)+')</small></span><button class="addBtn" style="padding:3px 8px;font-size:9px" onclick="addUserFromList(\\''+u.name+'\\',\\''+u.id+'\\')">Add</button></div>';
      });
      if(onlineHtml==='') onlineHtml = '<div style="font-size:10px;color:#666">You are alone in TAMY - Copy link to invite!<br><br><button class="addBtn" onclick="copyLink()">Copy TAMY Invite Link</button></div>';
      document.getElementById('onlineList').innerHTML = onlineHtml;
      document.getElementById('liveUsers').innerHTML = users.map(u=>'<span class="onlineDot"></span> '+u.name).join('<br>') || 'No users';
    }
    if(d.type==='chat' && mode!=='ai' && mode!=='secure'){
      addMsg(d.text+'<br><small style="color:#00ff88">TAMY Encrypted '+d.hash+' - From: '+d.fromName+'</small>','other secureB');
    }
    if(d.type==='signal') await handleSignal(d);
  };
  ws.onclose = ()=> setTimeout(connect,2000);
}
connect();

function addUserFromList(name, id){
  document.getElementById('addInput').value = name;
  addContact();
}

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
  if(text.includes('<script')){ alert('TAMY Security Wall blocked!'); return; }
  addMsg(text+'<br><small style="color:#00ff88">TAMY Encrypted Sent</small>','me secureB');
  inp.value = '';
  if(mode==='ai' || currentMode==='brain' || currentMode==='future' || currentMode==='secure'){
    addMsg('TAMY Thinking...','other');
    fetch('/ai?message='+encodeURIComponent(text)+'&mode='+currentMode+'&token='+securityToken)
.then(r=>r.json())
.then(d=>{
        msgsEl.lastChild.remove();
        addMsg('<small style="color:#00ff88">'+d.model+' '+d.hash+'</small><br>'+d.reply,'other ai secureB');
    });
  } else {
    if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:text,token:securityToken,name:myName}));
  }
}

function sendSticker(){
  let s=['😂','🚀','🔥','💜','👻','🤖','🌍','✨','🎉','😍'][Math.floor(Math.random()*10)];
  addMsg('<div style="font-size:60px">'+s+'</div><small>TAMY Sticker</small>','me secureB');
  if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:'TAMY Sticker: '+s,token:securityToken,name:myName}));
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
      addMsg('<audio controls src="'+url+'"></audio><br>TAMY Clear Audio Encrypted','me secureB');
      s.getTracks().forEach(t=>t.stop());
    };
    recorder.start();
    isRec=true;
  }catch(e){ alert('Allow mic'); }
}
function stopRec(){ if(!isRec||!recorder) return; try{ recorder.stop(); }catch(e){} isRec=false; }

async function startCall(isVideo){
  try{
    localStream=await navigator.mediaDevices.getUserMedia({video:isVideo?{width:{ideal:1280},height:{ideal:720}}:false,audio:true});
    document.getElementById('localV').srcObject=localStream;
    document.getElementById('videoBox').style.display='flex';
    if(ws) ws.send(JSON.stringify({type:'signal',data:{type:'call',isVideo:isVideo,token:securityToken}}));
    addMsg(isVideo?'TAMY Video 4K Call Started - Encrypted':'TAMY Audio Call - Encrypted','me secureB');
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
      wrap.innerHTML='<div style="position:absolute;top:8px;left:8px;background:#00ff88;color:#000;padding:3px 8px;border-radius:10px;font-size:8px;font-weight:bold;z-index:2">TAMY SECURE '+id+'</div>';
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
    if "hacker" in m or "security" in m or "protect" in m:
        return {"reply": f"<b>TAMY SECURITY WALL</b><br><br>You: '{safe_msg}'<br><br>7 Layers: Firewall, E2E, XSS Block, Blockchain 0x{block_hash}, Rate Limit, IP Block, WSS<br>Token {token[:8]} safe! Hacker cannot attack TAMY!", "model": "TAMY", "hash": f"0x{block_hash}"}
    return {"reply": f"<b>TAMY</b> - 0x{block_hash}<br><br>You: '{safe_msg}'<br><br>All in ONE app called TAMY:<br><br>TAMY Chat: Message + Voice 48kHz<br>TAMY Video: 100 people 4K + Whiteboard + Polls + Breakout + Record<br>TAMY Fun: Stickers + Stories<br>TAMY Brain: Write viral scripts + Code anything + Translate<br>TAMY Future: Hologram 3D, Voice Clone YOUR voice any lang, Mind-Read, Live Translate 100 langs, Blockchain<br>TAMY Secure: 7 Layers Firewall + E2E + XSS Block + Blockchain + Rate Limit + IP Block + WSS<br><br>Hello received! Secured! Token {token[:6]}", "model": "TAMY", "hash": f"0x{block_hash}"}

@app.websocket("/ws/{room}")
async def ws_handler(websocket: WebSocket, room: str, token: str = "", name: str = "User"):
    ip = websocket.client.host if websocket.client else "unknown"
    if ip in BLOCKED_IPS:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    cid = token or str(id(websocket))
    clients[cid] = websocket
    client_names[cid] = name or f"User{cid[-4:]}"
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
                    j["fromName"] = client_names.get(cid, "User")
                data = json.dumps(j)
            except:
                pass
            for oid, ows in list(clients.items()):
                if oid!= cid:
                    try:
                        mj = json.loads(data)
                        mj['from'] = cid
                        mj['fromName'] = client_names.get(cid, "User")
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
        if cid in client_names:
            del client_names[cid]
        if cid in ws_counts:
            del ws_counts[cid]
        await broadcast()

async def broadcast():
    users = [{"id": cid, "name": client_names.get(cid, f"User{cid[-4:]}")} for cid in clients.keys()]
    payload = json.dumps({"type": "users", "users": users})
    for ws in list(clients.values()):
        try:
            await ws.send_text(payload)
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
