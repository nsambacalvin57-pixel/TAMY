from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, json, time, hashlib, html
from collections import defaultdict

app = FastAPI(title="TAMY")
request_counts = defaultdict(list)
BLOCKED_IPS = set()

def sanitize_input(t: str) -> str:
    if not t: return ""
    t = html.escape(t)
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
        return JSONResponse(status_code=403, content={"error": "Blocked"})
    resp = await call_next(request)
    return resp

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
clients = {}
client_names = {}
client_numbers = {}
ws_counts = defaultdict(list)

HTML = """<!DOCTYPE html><html><head><title>TAMY</title><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"><style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial}body{height:100vh;background:#050508;color:#fff;overflow:hidden;display:flex;flex-direction:column}
#loginScreen{position:fixed;inset:0;background:linear-gradient(135deg,#050508,#0a0a14,#151528);z-index:200;display:flex;align-items:center;justify-content:center;padding:15px}
.loginBox{background:#12122a;border:2px solid #7c3aed;border-radius:20px;padding:25px;width:380px;box-shadow:0 0 40px #7c3aed55;text-align:center}
.loginBox h1{font-size:48px;font-weight:900;letter-spacing:12px;background:linear-gradient(90deg,#7c3aed,#00ff88,#ff00aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.loginBox small{color:#00ff88;font-size:11px;display:block;margin:10px 0 15px 0}
.loginBox input{width:100%;padding:12px;border-radius:10px;border:1px solid #2a2a4a;background:#0a0a14;color:#fff;outline:none;margin-bottom:10px;font-size:13px}
.loginBtn{width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(90deg,#7c3aed,#00ff88);color:#000;font-weight:900;cursor:pointer;margin-bottom:8px}
.loginBtn.sec{background:#1a1a2e;color:#fff;border:1px solid #2a2a4a}
#inviteModal{position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:150;display:none;align-items:center;justify-content:center;padding:15px}
.inviteBox{background:#12122a;border:2px solid #ff00aa;border-radius:20px;padding:20px;width:400px;max-width:95%;box-shadow:0 0 40px #ff00aa55;max-height:90vh;overflow-y:auto}
#topNav{height:60px;background:#0a0a14;border-bottom:1px solid #1e1e3a;display:flex;align-items:center;justify-content:space-between;padding:0 12px}
#logo{font-size:36px;font-weight:900;letter-spacing:10px;background:linear-gradient(90deg,#7c3aed,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pill{padding:7px 12px;border-radius:20px;background:#1a1a2e;border:1px solid #2a2a4a;font-size:11px;cursor:pointer}
.pill.voice{background:#00ff8820;border-color:#00ff88;color:#00ff88;font-weight:bold}
.pill.ultra{background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff;font-weight:900}
.pill.invite{background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;font-weight:900;border-color:#00ff88;animation:glow 2s infinite}
@keyframes glow{0%{box-shadow:0 0 5px #00ff88}50%{box-shadow:0 0 20px #ff00aa}100%{box-shadow:0 0 5px #00ff88}}
#main{flex:1;display:flex;overflow:hidden}
#left{width:330px;background:#0a0a12;border-right:1px solid #1e1e3a;display:flex;flex-direction:column}
.modes{display:grid;grid-template-columns:1fr 1fr;gap:6px;padding:8px}
.mode{padding:11px;border-radius:10px;background:#12122a;border:1px solid #1e1e3a;cursor:pointer;text-align:center}
.mode.active{background:linear-gradient(135deg,#7c3aed,#00ff88);color:#000}
.contacts{flex:1;overflow-y:auto;padding:6px}
.contact{padding:9px;border-radius:9px;display:flex;gap:8px;align-items:center;cursor:pointer;margin-bottom:4px;background:#0f0f1e;border:1px solid transparent}
.contact.active{border-color:#7c3aed;background:#1a1a3a}
.avatar{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;background:linear-gradient(135deg,#7c3aed,#00ff88)}
.addBox{padding:8px;background:#08080f;display:flex;flex-direction:column;gap:6px;border-top:1px solid #1e1e3a;border-bottom:1px solid #1e1e3a}
.addBoxRow{display:flex;gap:5px}
.addBox input{flex:1;padding:8px;border-radius:7px;border:1px solid #2a2a4a;background:#12122a;color:#fff;outline:none;font-size:11px}
.addBtn{padding:8px 12px;border-radius:7px;background:#00ff88;color:#000;border:none;font-weight:bold;cursor:pointer;font-size:11px}
#center{flex:1;display:flex;flex-direction:column;position:relative;background:#0a0a12}
#centerTop{padding:10px 12px;background:#0a0a14;border-bottom:1px solid #1e1e3a;display:flex;justify-content:space-between;align-items:center}
#msgs{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px}
.bubble{max-width:75%;padding:10px 12px;border-radius:14px;font-size:13px;word-break:break-word}
.me{align-self:flex-end;background:linear-gradient(135deg,#7c3aed,#4f46e5)}
.other{align-self:flex-start;background:#1e1e3a;border:1px solid #2a2a4a}
#right{width:285px;background:#08080f;border-left:1px solid #1e1e3a;display:flex;flex-direction:column;padding:10px;gap:8px;overflow-y:auto}
.panel{background:#12122a;border-radius:10px;padding:10px;border:1px solid #1e1e3a}
.panel b{font-size:11px;display:block;margin-bottom:6px;color:#a78bfa}
.toolBtn{width:100%;padding:9px;border-radius:8px;border:1px solid #2a2a4a;background:#1a1a3a;color:#fff;cursor:pointer;margin-bottom:5px;font-size:11px;display:flex;gap:6px;align-items:center;text-align:left}
#voiceBox{display:none;position:absolute;inset:0;background:linear-gradient(135deg,#0a0a14,#1a1a3a);z-index:50;flex-direction:column;align-items:center;justify-content:center}
#videoBox{display:none;position:absolute;inset:0;background:#000;z-index:50;flex-direction:column}
#videoGrid{flex:1;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px;padding:8px;background:#000;overflow-y:auto}
.videoTile{position:relative;background:#0f0f1e;border-radius:12px;overflow:hidden;border:2px solid #1e1e3a;aspect-ratio:16/9}
.videoTile video{width:100%;height:100%;object-fit:cover}
#vControls{padding:10px;background:#0a0a14;display:flex;justify-content:center;gap:8px;flex-wrap:wrap;border-top:1px solid #1e1e3a}
.vb{padding:9px 14px;border-radius:18px;border:none;font-weight:bold;cursor:pointer;background:#1a1a2e;color:#fff;font-size:11px}
.vb.end{background:#ff0040!important}
.vb.voice{background:#00ff88!important;color:#000!important}
.vb.ultra{background:linear-gradient(90deg,#ff00aa,#7c3aed)!important;color:#fff!important}
#inputArea{padding:8px 10px;background:#0a0a14;border-top:1px solid #1e1e3a;display:flex;gap:6px;align-items:center}
#inputArea input{flex:1;padding:10px 14px;border-radius:18px;border:1px solid #2a2a4a;background:#12122a;color:#fff;outline:none}
.iconBtn{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;background:#1a1a2e;border:1px solid #2a2a4a;color:#fff}
.sendBtn{background:linear-gradient(135deg,#7c3aed,#00ff88)!important;border:none!important;color:#000!important}
#secAlert{position:fixed;top:70px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:8px 16px;border-radius:20px;font-size:11px;font-weight:bold;z-index:300;display:none}
.userRow{display:flex;justify-content:space-between;align-items:center;padding:6px 8px;background:#0f0f1e;border-radius:8px;margin-bottom:4px;font-size:11px}
.onlineDot{width:7px;height:7px;background:#00ff88;border-radius:50%;display:inline-block}
</style></head><body>

<div id="loginScreen">
<div class="loginBox">
<h1>TAMY</h1>
<small>TAMY Sign In + Contact Number + Add Friends Invite</small>
<input id="loginName" placeholder="Your TAMY Name - ex: Ahmed">
<input id="loginNumber" placeholder="Your Contact Number - ex: +966 512345678" type="tel">
<input id="loginId" placeholder="Your TAMY ID - ex: tamy_123">
<input id="loginPass" type="password" placeholder="Password - min 4 digits">
<button class="loginBtn" onclick="doLogin()">Sign In to TAMY</button>
<button class="loginBtn sec" onclick="createNewId()">Create New TAMY ID</button>
<div style="margin-top:8px;font-size:10px;color:#888">App name: TAMY only</div>
<div id="loginMsg" style="margin-top:8px;font-size:11px;color:#00ff88"></div>
</div>
</div>

<div id="inviteModal">
<div class="inviteBox">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><b style="color:#ff00aa;font-size:14px"><i class="fa-solid fa-user-plus"></i> TAMY Add Friends / Invite</b><button onclick="closeInvite()" style="background:#ff0040;color:#fff;border:none;border-radius:50%;width:28px;height:28px;cursor:pointer">X</button></div>

<div style="background:#000;border-radius:10px;padding:10px;border:1px dashed #ff00aa;margin-bottom:10px">
<div style="font-size:10px;color:#ff00aa;font-weight:bold;margin-bottom:6px">YOUR TAMY INVITE LINK - Share to Add Friends</div>
<div id="inviteLinkText" style="font-size:11px;color:#00ff88;word-break:break-all;background:#0a0a14;padding:8px;border-radius:8px;border:1px solid #1e1e3a">Loading...</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
<button class="addBtn" onclick="copyInviteLink()" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff"><i class="fa-solid fa-link"></i> Copy Invite Link</button>
<button class="addBtn" onclick="shareWhatsApp()" style="background:#25D366;color:#fff"><i class="fa-brands fa-whatsapp"></i> WhatsApp Invite</button>
</div>
</div>

<div style="background:#0a0a14;border-radius:10px;padding:10px;border:1px solid #1e1e3a;margin-bottom:10px">
<div style="font-size:10px;color:#00ff88;font-weight:bold;margin-bottom:6px">Add Friend by Name + Contact Number</div>
<div style="display:flex;gap:6px;margin-bottom:6px"><input id="inviteName" placeholder="Friend Name - ex: Ali" style="flex:1;padding:8px;border-radius:7px;border:1px solid #2a2a4a;background:#000;color:#fff;font-size:11px"><input id="inviteNumber" placeholder="Number +966..." type="tel" style="flex:1;padding:8px;border-radius:7px;border:1px solid #2a2a4a;background:#000;color:#fff;font-size:11px"></div>
<button class="addBtn" style="width:100%;background:#00ff88;color:#000" onclick="inviteByNumber()"><i class="fa-solid fa-user-plus"></i> Add Friend with Number to TAMY</button>
</div>

<div style="background:#0a0a14;border-radius:10px;padding:10px;border:1px solid #1e1e3a">
<div style="font-size:10px;color:#a78bfa;font-weight:bold;margin-bottom:6px">Add Friend by TAMY ID</div>
<div style="display:flex;gap:6px"><input id="inviteId" placeholder="Friend TAMY ID - tamy_xxx" style="flex:1;padding:8px;border-radius:7px;border:1px solid #2a2a4a;background:#000;color:#fff;font-size:11px"><button class="addBtn" onclick="inviteById()"><i class="fa-solid fa-plus"></i> Add</button></div>
</div>

</div>
</div>

<div id="secAlert"></div>
<div id="topNav"><div id="logo">TAMY</div><div style="display:flex;gap:6px;align-items:center"><div class="pill" style="background:#00ff8820;border-color:#00ff88;color:#00ff88">WALL ON</div><div id="liveCount" class="pill">0 Online</div></div><div style="display:flex;gap:6px"><button class="pill invite" onclick="openInvite()"><i class="fa-solid fa-user-plus"></i> Add Friends / Invite</button><button class="pill voice" onclick="startVoiceCall()">VOICE</button><button class="pill ultra" onclick="startVideoCall()">VIDEO 4K ULTRA HD</button><button class="pill" onclick="doLogout()" style="background:#ff004020;color:#ff0040">Logout</button></div></div>
<div id="main">
<div id="left">
<div class="modes">
<div class="mode active" onclick="setMode('chat',this)"><i class="fa-solid fa-comment-dots"></i><b>TAMY CHAT</b></div>
<div class="mode" onclick="setMode('voice',this)"><i class="fa-solid fa-phone"></i><b>TAMY VOICE</b></div>
<div class="mode" onclick="setMode('video',this)"><i class="fa-solid fa-video"></i><b>TAMY VIDEO 4K ULTRA HD</b></div>
<div class="mode" onclick="setMode('fun',this)"><i class="fa-solid fa-face-smile"></i><b>TAMY FUN</b></div>
<div class="mode" onclick="setMode('brain',this)"><i class="fa-solid fa-brain"></i><b>TAMY BRAIN</b></div>
<div class="mode" onclick="setMode('future',this)"><i class="fa-solid fa-rocket"></i><b>TAMY FUTURE</b></div>
</div>

<div class="addBox">
<div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:10px;color:#00ff88;font-weight:bold">Add TAMY Contact - Name + Number</div><button class="addBtn" style="padding:3px 8px;font-size:9px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()">Invite</button></div>
<div class="addBoxRow"><input id="addName" placeholder="Contact Name"><input id="addNumber" placeholder="Number +966..." type="tel"></div>
<div class="addBoxRow"><button class="addBtn" style="flex:1" onclick="addContact()"><i class="fa-solid fa-user-plus"></i> Add Contact with Number</button></div>
</div>

<div id="contactsList" class="contacts">
<div class="contact active" onclick="openChat('TAMY','T','ai','')"><div class="avatar">T</div><div style="flex:1"><b>TAMY</b><div style="font-size:10px;color:#00ff88">AI - 4K Ultra HD</div></div></div>
<div class="contact" onclick="openChat('TAMY MEET 4K ULTRA HD','M','group','')"><div class="avatar" style="background:linear-gradient(135deg,#ff00aa,#7c3aed)">M</div><div style="flex:1"><b>TAMY MEET 4K ULTRA HD</b><div style="font-size:10px;color:#ff00aa">100 people 4K Ultra HD</div></div><div id="gCount" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff;padding:3px 7px;border-radius:8px;font-size:9px">0</div></div>
</div>

<div style="padding:8px;background:#08080f;border-top:1px solid #1e1e3a;max-height:160px;overflow-y:auto">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px"><div style="font-size:10px;color:#ff00aa;font-weight:bold">TAMY ONLINE FRIENDS - Invite</div><button class="addBtn" style="padding:2px 6px;font-size:8px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()">Add Friends</button></div>
<div id="onlineList" style="font-size:11px;color:#aaa">No friends online - Click Add Friends / Invite to invite!</div>
</div>
</div>

<div id="center">
<div id="centerTop"><div style="display:flex;gap:8px;align-items:center"><div class="avatar" id="hAv">T</div><div><b id="hName">TAMY</b><div id="hNumber" style="font-size:11px;color:#00ff88;font-weight:bold"></div><small style="color:#00ff88;font-size:10px">TAMY 4K Ultra HD • Add Friends</small></div></div><div style="display:flex;gap:6px"><button class="pill invite" onclick="openInvite()"><i class="fa-solid fa-user-plus"></i> Add Friends</button><button class="pill voice" onclick="startVoiceCall()">VOICE</button><button class="pill ultra" onclick="startVideoCall()">4K ULTRA HD</button></div></div>

<div id="voiceBox"><div style="text-align:center"><div class="avatar" style="width:110px;height:110px;font-size:45px;margin:0 auto 15px;background:linear-gradient(135deg,#00ff88,#7c3aed)">T</div><h2 id="voiceStatus">TAMY VOICE CALL</h2><p id="voiceTimer" style="margin:10px;color:#00ff88;font-size:18px">00:00</p><p id="voiceNumber" style="color:#ff00aa;font-size:13px;font-weight:bold"></p><p style="color:#aaa;font-size:11px">Invite Friends • Encrypted • 48kHz HD</p><div style="margin-top:25px;display:flex;gap:10px;justify-content:center"><button class="vb voice" onclick="toggleMute()">Mute</button><button class="vb end" onclick="endVoiceCall()">End Voice</button></div></div></div>

<div id="videoBox"><div style="padding:10px 12px;background:linear-gradient(90deg,#0a0a14,#1a1a3a);display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #ff00aa"><div><b style="background:linear-gradient(90deg,#ff00aa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent">TAMY VIDEO 4K ULTRA HD</b><br><small style="color:#00ff88">3840x2160 60fps HDR • Add Friends</small></div><div class="pill ultra" style="font-size:9px">4K ULTRA HD BEST</div></div><div id="videoGrid"><div class="videoTile" style="border-color:#ff00aa"><video id="localV" autoplay muted playsinline></video></div><div id="remoteBox" style="display:contents"></div></div><div id="vControls"><button class="vb voice" onclick="toggleMute()">Mute</button><button class="vb" onclick="toggleCam()">Cam 4K Ultra HD</button><button class="vb" style="background:linear-gradient(90deg,#00ff88,#ff00aa)!important;color:#000" onclick="openInvite()">Invite Friends</button><button class="vb end" onclick="endVideoCall()">End 4K Ultra HD</button></div></div>

<div id="msgs"></div>
<div id="inputArea"><button class="iconBtn" onclick="startVoiceCall()" style="background:#00ff8820;color:#00ff88;border-color:#00ff88"><i class="fa-solid fa-phone"></i></button><button class="iconBtn" onclick="openInvite()" style="background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;border-color:#00ff88"><i class="fa-solid fa-user-plus"></i></button><input id="inp" placeholder="Type hello... Invite friends!" onkeypress="if(event.key==='Enter')sendText()"><button class="iconBtn sendBtn" onclick="sendText()"><i class="fa-solid fa-paper-plane"></i></button></div>
</div>

<div id="right">
<div class="panel" style="border-color:#00ff88;background:linear-gradient(135deg,#00ff8810,#ff00aa10)"><b style="color:#00ff88">TAMY Add Friends / Invite - NEW!</b>
<button class="toolBtn" style="background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;font-weight:900;border-color:#00ff88" onclick="openInvite()"><i class="fa-solid fa-user-plus"></i> Add Friends / Invite - Click Here</button>
<button class="toolBtn" style="border-color:#ff00aa;color:#ff00aa" onclick="copyInviteLink()"><i class="fa-solid fa-link"></i> Copy TAMY Invite Link</button>
<button class="toolBtn" style="border-color:#25D366;color:#25D366" onclick="shareWhatsApp()"><i class="fa-brands fa-whatsapp"></i> Invite via WhatsApp</button>
<button class="toolBtn" style="border-color:#00ff88;color:#00ff88" onclick="openInvite()"><i class="fa-solid fa-address-book"></i> Add Friend by Contact Number</button>
</div>
<div class="panel" style="border-color:#ff00aa"><b style="color:#ff00aa">My TAMY Account + Number</b><div id="myIdBox" style="padding:8px;background:#000;border-radius:8px;font-size:11px;word-break:break-all;border:1px dashed #ff00aa"></div></div>
<div class="panel"><b>TAMY Live Friends - Number + Invite</b><div id="liveUsers" style="font-size:11px;color:#aaa">Connecting...</div></div>
</div>
</div>
<script>
let ws,mode='ai',pcs={},localStream=null,voiceTimerInt=null,voiceSeconds=0,isMuted=false;
const msgsEl=document.getElementById('msgs');
let securityToken=localStorage.getItem('tamy_token')||'';
let myName=localStorage.getItem('tamy_name')||'';
let myPass=localStorage.getItem('tamy_pass')||'';
let myNumber=localStorage.getItem('tamy_number')||'';
let myContacts=JSON.parse(localStorage.getItem('tamy_contacts')||'[]');

function showLogin(){
  document.getElementById('loginScreen').style.display='flex';
  if(myName) document.getElementById('loginName').value=myName;
  if(myNumber) document.getElementById('loginNumber').value=myNumber;
  if(securityToken) document.getElementById('loginId').value=securityToken;
  if(myPass) document.getElementById('loginPass').value=myPass;
}
function hideLogin(){document.getElementById('loginScreen').style.display='none';}
function createNewId(){
  let newId='tamy_'+Math.random().toString(36).substring(2,8);
  document.getElementById('loginId').value=newId;
  document.getElementById('loginMsg').innerText='New TAMY ID: '+newId;
  showAlert('New TAMY ID: '+newId);
}
function doLogin(){
  let name=document.getElementById('loginName').value.trim();
  let number=document.getElementById('loginNumber').value.trim();
  let id=document.getElementById('loginId').value.trim();
  let pass=document.getElementById('loginPass').value.trim();
  if(!name){alert('Type Name!');return;}
  if(!number){alert('Type Contact Number!');return;}
  if(!id){alert('Type TAMY ID or Create New!');return;}
  if(!pass || pass.length<4){alert('Password min 4!');return;}
  securityToken=id; myName=name; myNumber=number; myPass=pass;
  localStorage.setItem('tamy_token',securityToken);
  localStorage.setItem('tamy_name',myName);
  localStorage.setItem('tamy_number',myNumber);
  localStorage.setItem('tamy_pass',myPass);
  document.getElementById('myIdBox').innerHTML='Name: <b style="color:#00ff88">'+myName+'</b><br>Number: <b style="color:#ff00aa;font-size:13px">'+myNumber+'</b><br>ID: <b>'+securityToken+'</b><br>Pass: ****<br><span style="color:#00ff88">Friends Invite Ready</span>';
  document.getElementById('inviteLinkText').innerText=location.origin+'?invite='+securityToken+'&from='+encodeURIComponent(myName);
  hideLogin(); showAlert('Welcome '+myName+'! Invite friends now!'); connect(); openChat('TAMY','T','ai',''); loadContacts();
}
function doLogout(){
  if(confirm('Logout TAMY?')){
    localStorage.removeItem('tamy_token'); localStorage.removeItem('tamy_name'); localStorage.removeItem('tamy_number'); localStorage.removeItem('tamy_pass');
    securityToken=''; myName=''; myNumber=''; myPass='';
    document.getElementById('loginName').value=''; document.getElementById('loginNumber').value=''; document.getElementById('loginId').value=''; document.getElementById('loginPass').value='';
    showLogin(); if(ws) ws.close(); showAlert('Logged out');
  }
}
if(!securityToken ||!myName ||!myNumber){showLogin();}else{
  document.getElementById('myIdBox').innerHTML='Name: <b style="color:#00ff88">'+myName+'</b><br>Number: <b style="color:#ff00aa;font-size:13px">'+myNumber+'</b><br>ID: <b>'+securityToken+'</b><br><span style="color:#00ff88">4K Ultra HD • Friends Invite Ready</span>';
  document.getElementById('inviteLinkText').innerText=location.origin+'?invite='+securityToken+'&from='+encodeURIComponent(myName);
  hideLogin();
}

function openInvite(){
  document.getElementById('inviteLinkText').innerText=location.origin+'?invite='+securityToken+'&from='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNumber);
  document.getElementById('inviteModal').style.display='flex';
}
function closeInvite(){document.getElementById('inviteModal').style.display='none';}
function copyInviteLink(){
  let link=document.getElementById('inviteLinkText').innerText;
  navigator.clipboard.writeText(link).then(()=>{showAlert('TAMY Invite Link Copied! Send to friends!');});
}
function shareWhatsApp(){
  let link=document.getElementById('inviteLinkText').innerText;
  let text=encodeURIComponent('Join me on TAMY - Best Chat + Voice + Video 4K Ultra HD App! App name: TAMY Only! My Number: '+myNumber+' - Click to join: '+link);
  window.open('https://wa.me/?text='+text,'_blank');
  showAlert('Opening WhatsApp Invite!');
}
function inviteByNumber(){
  let name=document.getElementById('inviteName').value.trim() || document.getElementById('addName').value.trim();
  let number=document.getElementById('inviteNumber').value.trim() || document.getElementById('addNumber').value.trim();
  if(!name){alert('Type Friend Name!');return;}
  if(!number){alert('Type Friend Number!');return;}
  addContactDirect(name, number);
  document.getElementById('inviteName').value=''; document.getElementById('inviteNumber').value='';
  document.getElementById('addName').value=''; document.getElementById('addNumber').value='';
  closeInvite();
}
function inviteById(){
  let id=document.getElementById('inviteId').value.trim();
  if(!id){alert('Type Friend TAMY ID!');return;}
  addContactDirect(id, '+966 (ID: '+id+')');
  document.getElementById('inviteId').value='';
  closeInvite();
}

function addContactDirect(name, number){
  if(!name ||!number) return;
  let id=name.replace(/[^a-zA-Z0-9]/g,'').substring(0,12)||'friend'+Date.now();
  myContacts.push({name:name, number:number, id:id});
  localStorage.setItem('tamy_contacts', JSON.stringify(myContacts));
  let list=document.getElementById('contactsList');
  let div=document.createElement('div'); div.className='contact'; div.dataset.id=id;
  let av=name.charAt(0).toUpperCase();
  div.innerHTML='<div class="avatar" style="background:linear-gradient(135deg,#00ff88,#ff00aa)">'+av+'</div><div style="flex:1"><b>'+name+'</b><div style="font-size:11px;color:#00ff88;font-weight:bold"><i class="fa-solid fa-phone"></i> '+number+'</div><div style="font-size:9px;color:#a78bfa">TAMY Friend • Invite Sent</div></div><div style="display:flex;flex-direction:column;gap:3px"><button class="addBtn" style="padding:4px 6px;font-size:8px;background:#00ff88;color:#000" onclick="event.stopPropagation();startVoiceCall()"><i class="fa-solid fa-phone"></i></button><button class="addBtn" style="padding:4px 6px;font-size:8px;background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="event.stopPropagation();startVideoCall()">4K</button></div>';
  div.onclick=function(){openChat(name,av,'private',number); document.querySelectorAll('.contact').forEach(c=>c.classList.remove('active')); div.classList.add('active');};
  list.appendChild(div);
  showAlert('TAMY Friend '+name+' '+number+' Added!');
  addMsg('TAMY Friend Invited:<br>Name: <b>'+name+'</b><br>Number: <b style="color:#00ff88">'+number+'</b><br>Invite Link: <b style="color:#ff00aa">'+location.origin+'?invite='+securityToken+'</b><br>Share link to '+name+' to join TAMY!','other');
}
function loadContacts(){
  myContacts.forEach(c=>{
    let list=document.getElementById('contactsList');
    if(document.querySelector('[data-id="'+c.id+'"]')) return;
    let div=document.createElement('div'); div.className='contact'; div.dataset.id=c.id;
    let av=c.name.charAt(0).toUpperCase();
    div.innerHTML='<div class="avatar" style="background:linear-gradient(135deg,#00ff88,#ff00aa)">'+av+'</div><div style="flex:1"><b>'+c.name+'</b><div style="font-size:11px;color:#00ff88;font-weight:bold"><i class="fa-solid fa-phone"></i> '+c.number+'</div><div style="font-size:9px;color:#a78bfa">TAMY Friend</div></div><div style="display:flex;flex-direction:column;gap:3px"><button class="addBtn" style="padding:4px 6px;font-size:8px;background:#00ff88;color:#000" onclick="event.stopPropagation();startVoiceCall()"><i class="fa-solid fa-phone"></i></button><button class="addBtn" style="padding:4px 6px;font-size:8px;background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="event.stopPropagation();startVideoCall()">4K</button></div>';
    div.onclick=function(){openChat(c.name,av,'private',c.number); document.querySelectorAll('.contact').forEach(x=>x.classList.remove('active')); div.classList.add('active');};
    list.appendChild(div);
  });
}

function showAlert(m){let e=document.getElementById('secAlert');e.innerText=m;e.style.display='block';setTimeout(()=>e.style.display='none',3000);}
function copyLink(){copyInviteLink();}

function addContact(){
  let nameEl=document.getElementById('addName'); let numEl=document.getElementById('addNumber');
  let name=nameEl.value.trim(); let number=numEl.value.trim();
  if(!name){alert('Type Contact Name!');return;}
  if(!number){alert('Type Contact Number!');return;}
  addContactDirect(name, number);
  nameEl.value=''; numEl.value='';
}

function setMode(m,el){
  currentMode=m; document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active')); el.classList.add('active');
  if(m==='voice'){openChat('TAMY VOICE','V','group',''); startVoiceCall();}
  else if(m==='video'){openChat('TAMY VIDEO 4K ULTRA HD','V','group',''); startVideoCall();}
  else if(m==='chat') openChat('TAMY CHAT','C','group','');
  else if(m==='fun') openChat('TAMY FUN','F','fun','');
  else if(m==='brain') openChat('TAMY BRAIN','B','ai','');
  else if(m==='future') openChat('TAMY FUTURE','F','ai','');
}
function openChat(name,av,m,number){
  mode=m==='private'?'group':m==='fun'?'fun':m==='ai'?'ai':'group';
  document.getElementById('hName').innerText=name; document.getElementById('hAv').innerText=av;
  document.getElementById('hNumber').innerHTML=number? '<i class="fa-solid fa-phone"></i> Contact Number: <b>'+number+'</b>' : (m==='ai'?'<i class="fa-solid fa-phone"></i> Your Number: <b>'+myNumber+'</b>':'');
  msgsEl.innerHTML='';
  if(m==='ai') addMsg('Welcome <b>'+myName+'</b> to <b>TAMY</b><br><br>Your Number: <b style="color:#ff00aa;font-size:14px">'+myNumber+'</b><br>ID: '+securityToken+'<br><br>New: Add Friends / Invite!<br>• Copy Invite Link<br>• Invite via WhatsApp<br>• Add Friend by Number<br>• Add Friend by TAMY ID<br><br><button class="addBtn" style="background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()"><i class="fa-solid fa-user-plus"></i> Add Friends / Invite Now</button>','other');
  else addMsg('Chat with <b>'+name+'</b>'+(number?'<br>Number: <b style="color:#00ff88;font-size:14px">'+number+'</b>':'')+'<br><br><button class="addBtn" style="background:#00ff88;color:#000" onclick="startVoiceCall()"><i class="fa-solid fa-phone"></i> VOICE CALL</button> <button class="addBtn" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="startVideoCall()"><i class="fa-solid fa-video"></i> VIDEO 4K ULTRA HD</button> <button class="addBtn" style="background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()"><i class="fa-solid fa-user-plus"></i> Invite More</button>','other');
}
function getWsUrl(){return (location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws/tamy?token='+securityToken+'&name='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNumber);}
function connect(){
  if(!securityToken) return;
  if(ws) try{ws.close();}catch(e){}
  ws=new WebSocket(getWsUrl());
  ws.onopen=()=>{document.getElementById('liveUsers').innerHTML='Signed in: <b>'+myName+'</b><br>Number: <b style="color:#ff00aa">'+myNumber+'</b><br>ID: '+securityToken.substring(0,8)+'<br><button class="addBtn" style="margin-top:6px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()"><i class="fa-solid fa-user-plus"></i> Invite Friends</button>';document.getElementById('liveCount').innerText='LIVE 4K ULTRA HD';showAlert('TAMY Signed In - Invite Ready!');};
  ws.onmessage=async e=>{
    let d=JSON.parse(e.data);
    if(d.type==='users'){
      let users=d.users||[];
      document.getElementById('liveCount').innerText=users.length+' Online';
      let g=document.getElementById('gCount'); if(g) g.innerText=users.length;
      let html='';
      users.forEach(u=>{
        if(u.id===securityToken) return;
        html+='<div class="userRow"><div><span class="onlineDot"></span> <b>'+u.name+'</b><br><span style="color:#00ff88;font-size:11px"><i class="fa-solid fa-phone"></i> '+(u.number||'No number')+'</span></div><div style="display:flex;gap:3px;flex-direction:column"><button class="addBtn" style="padding:3px 6px;font-size:8px;background:#00ff88;color:#000" onclick="addContactDirect(\\''+u.name+'\\',\\''+(u.number||'')+'\\')"><i class="fa-solid fa-user-plus"></i></button><button class="addBtn" style="padding:3px 6px;font-size:8px;background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="startVideoCall()">4K</button></div></div>';
      });
      if(html==='') html='<div style="font-size:10px;color:#666">No friends online - Invite them!<br><button class="addBtn" style="margin-top:6px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()"><i class="fa-solid fa-user-plus"></i> Add Friends / Invite</button><br><br><button class="addBtn" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="copyInviteLink()"><i class="fa-solid fa-link"></i> Copy Invite Link</button></div>';
      document.getElementById('onlineList').innerHTML=html;
      document.getElementById('liveUsers').innerHTML=users.map(u=>'<span class="onlineDot"></span> '+u.name+'<br><small style="color:#00ff88">'+(u.number||'')+'</small>').join('<br>')||'No friends online<br><button class="addBtn" style="margin-top:4px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;font-size:9px" onclick="openInvite()">Invite Friends</button>';
    }
    if(d.type==='chat') addMsg(d.text+'<br><small style="color:#ff00aa">From: '+d.fromName+' '+(d.fromNumber||'')+'</small>','other');
    if(d.type==='signal') await handleSignal(d);
  };
  ws.onclose=()=>{if(securityToken) setTimeout(connect,2000);};
}
function addMsg(h,c){let t=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});let div=document.createElement('div');div.className='bubble '+c;div.innerHTML=h+'<div style="text-align:right;font-size:9px;opacity:0.5">'+t+'</div>';msgsEl.appendChild(div);msgsEl.scrollTop=msgsEl.scrollHeight;}
function sendText(){
  let inp=document.getElementById('inp');let text=inp.value.trim();if(!text)return;
  addMsg(text+'<br><small style="color:#00ff88"><i class="fa-solid fa-phone"></i> '+myNumber+'</small>','me');inp.value='';
  if(mode==='ai' || currentMode==='brain' || currentMode==='future'){
    addMsg('TAMY Thinking...','other');
    fetch('/ai?message='+encodeURIComponent(text)+'&mode='+currentMode+'&token='+securityToken).then(r=>r.json()).then(d=>{msgsEl.lastChild.remove();addMsg(d.reply,'other');});
  }else{
    if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:text,token:securityToken,name:myName,number:myNumber}));
  }
}
async function startVoiceCall(){
  try{
    localStream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,sampleRate:48000},video:false});
    document.getElementById('voiceBox').style.display='flex';
    document.getElementById('voiceStatus').innerText='TAMY VOICE CALL';
    document.getElementById('voiceNumber').innerHTML='Your Number: <b>'+myNumber+'</b>';
    voiceSeconds=0;document.getElementById('voiceTimer').innerText='00:00';
    voiceTimerInt=setInterval(()=>{voiceSeconds++;let m=String(Math.floor(voiceSeconds/60)).padStart(2,'0');let s=String(voiceSeconds%60).padStart(2,'0');document.getElementById('voiceTimer').innerText=m+':'+s;},1000);
    if(ws) ws.send(JSON.stringify({type:'signal',data:{type:'voice_call',fromName:myName,fromNumber:myNumber},token:securityToken,number:myNumber}));
    addMsg('TAMY VOICE CALL Started - Number: '+myNumber,'me');
  }catch(e){alert('Allow mic: '+e.message);}
}
async function startVideoCall(){
  try{
    localStream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:3840},height:{ideal:2160},frameRate:{ideal:60}},audio:true});
    document.getElementById('localV').srcObject=localStream;
    document.getElementById('videoBox').style.display='flex';
    if(ws) ws.send(JSON.stringify({type:'signal',data:{type:'call',fromName:myName,fromNumber:myNumber},token:securityToken,number:myNumber}));
    addMsg('TAMY VIDEO 4K ULTRA HD Started - Number: '+myNumber,'me');
  }catch(e){
    try{
      localStream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1920},height:{ideal:1080}},audio:true});
      document.getElementById('localV').srcObject=localStream;
      document.getElementById('videoBox').style.display='flex';
      if(ws) ws.send(JSON.stringify({type:'signal',data:{type:'call',fromName:myName,fromNumber:myNumber},token:securityToken,number:myNumber}));
    }catch(e2){alert('Allow cam mic: '+e2.message);}
  }
}
function createPC(id){
  let pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});
  pc.onicecandidate=e=>{if(e.candidate&&ws) ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate},token:securityToken,number:myNumber}));};
  pc.ontrack=e=>{
    let wrapId='wrap-'+id;
    let wrap=document.getElementById(wrapId);
    if(!wrap){
      wrap=document.createElement('div');wrap.id=wrapId;wrap.className='videoTile';wrap.style.borderColor='#ff00aa';
      wrap.innerHTML='<div style="position:absolute;top:6px;left:6px;background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff;padding:4px 10px;border-radius:10px;font-size:9px">TAMY 4K FRIEND</div>';
      let v=document.createElement('video');v.id='remote-'+id;v.autoplay=true;v.playsInline=true;wrap.appendChild(v);
      document.getElementById('remoteBox').appendChild(wrap);
    }
    document.getElementById('remote-'+id).srcObject=e.streams[0];
  };
  if(localStream) localStream.getTracks().forEach(t=>pc.addTrack(t,localStream));
  pcs[id]=pc;return pc;
}
async function handleSignal(d){
  let from=d.from||'peer';let data=d.data||{};
  if(data.type==='voice_call'){
    try{
      localStream=await navigator.mediaDevices.getUserMedia({audio:true,video:false});
      document.getElementById('voiceBox').style.display='flex';
      document.getElementById('voiceStatus').innerText='TAMY VOICE CALL Incoming';
      document.getElementById('voiceNumber').innerHTML='From: <b>'+(d.fromName||from)+'</b><br>Number: <b style="color:#00ff88">'+(d.fromNumber||'')+'</b>';
      voiceSeconds=0;voiceTimerInt=setInterval(()=>{voiceSeconds++;let m=String(Math.floor(voiceSeconds/60)).padStart(2,'0');let s=String(voiceSeconds%60).padStart(2,'0');document.getElementById('voiceTimer').innerText=m+':'+s;},1000);
      let pc=createPC(from);let off=await pc.createOffer();await pc.setLocalDescription(off);
      ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,token:securityToken,number:myNumber}));
    }catch(e){}
  }else if(data.type==='call'){
    try{
      localStream=await navigator.mediaDevices.getUserMedia({video:true,audio:true});
      document.getElementById('localV').srcObject=localStream;
      document.getElementById('videoBox').style.display='flex';
      let pc=createPC(from);let off=await pc.createOffer();await pc.setLocalDescription(off);
      ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,token:securityToken,number:myNumber}));
    }catch(e){}
  }else if(data.type==='offer'){
    let pc=createPC(from);await pc.setRemoteDescription(new RTCSessionDescription(data));
    let ans=await pc.createAnswer();await pc.setLocalDescription(ans);
    ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,token:securityToken,number:myNumber}));
  }else if(data.type==='answer'){
    let pc=pcs[from];if(pc)await pc.setRemoteDescription(new RTCSessionDescription(data));
  }else if(data.candidate){
    for(let k in pcs){try{await pcs[k].addIceCandidate(new RTCIceCandidate(data.candidate));}catch(e){}}
  }
}
function endVoiceCall(){
  document.getElementById('voiceBox').style.display='none';
  if(voiceTimerInt)clearInterval(voiceTimerInt);voiceSeconds=0;
  if(localStream){localStream.getTracks().forEach(t=>t.stop());localStream=null;}
  for(let k in pcs){try{pcs[k].close();}catch(e){}}pcs={};document.getElementById('remoteBox').innerHTML='';
}
function endVideoCall(){
  document.getElementById('videoBox').style.display='none';
  if(localStream){localStream.getTracks().forEach(t=>t.stop());localStream=null;}
  for(let k in pcs){try{pcs[k].close();}catch(e){}}pcs={};document.getElementById('remoteBox').innerHTML='';
}
function toggleMute(){if(!localStream)return;isMuted=!isMuted;localStream.getAudioTracks().forEach(t=>t.enabled=!isMuted);showAlert(isMuted?'Mic Muted':'Mic On');}
function toggleCam(){if(!localStream)return;localStream.getVideoTracks().forEach(t=>t.enabled=!t.enabled);}
if(securityToken && myName && myNumber){connect(); openChat('TAMY','T','ai',''); loadContacts();}
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/ai")
def ai_endpoint(message: str = "", mode: str = "chat", token: str = ""):
    safe_msg = sanitize_input(message)
    block_hash = hashlib.sha256(f"{safe_msg}{time.time()}".encode()).hexdigest()[:8]
    return {"reply": f"<b>TAMY 4K ULTRA HD</b> 0x{block_hash}<br>You: '{safe_msg}'<br>TAMY Add Friends Invite Ready!<br>Hello!", "model": "TAMY", "hash": f"0x{block_hash}"}

@app.websocket("/ws/{room}")
async def ws_handler(websocket: WebSocket, room: str, token: str = "", name: str = "User", number: str = ""):
    ip = websocket.client.host if websocket.client else "unknown"
    if ip in BLOCKED_IPS:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    cid = token or str(id(websocket))
    clients[cid] = websocket
    client_names[cid] = name or f"User{cid[-4:]}"
    client_numbers[cid] = number or ""
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
                    j["fromNumber"] = client_numbers.get(cid, "")
                data = json.dumps(j)
            except:
                pass
            for oid, ows in list(clients.items()):
                if oid!= cid:
                    try:
                        mj = json.loads(data)
                        mj['from'] = cid
                        mj['fromName'] = client_names.get(cid, "User")
                        mj['fromNumber'] = client_numbers.get(cid, "")
                        await ows.send_text(json.dumps(mj))
                    except:
                        try:
                            await ows.send_text(data)
                        except:
                            pass
    except WebSocketDisconnect:
        pass
    finally:
        if cid in clients: del clients[cid]
        if cid in client_names: del client_names[cid]
        if cid in client_numbers: del client_numbers[cid]
        if cid in ws_counts: del ws_counts[cid]
        await broadcast()

async def broadcast():
    users = [{"id": cid, "name": client_names.get(cid, f"User{cid[-4:]}"), "number": client_numbers.get(cid, "")} for cid in clients.keys()]
    payload = json.dumps({"type": "users", "users": users})
    for ws in list(clients.values()):
        try:
            await ws.send_text(payload)
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
