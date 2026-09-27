from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn, json

app = FastAPI()
clients = {}

HTML = """
<!DOCTYPE html><html><head>
<title>TAMY - Chat, Call, Video</title>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}
body{display:flex;height:100vh;background:#0f0f0f;color:#fff;overflow:hidden}
#sidebar{width:32%;min-width:260px;background:#161616;border-right:1px solid #222;display:flex;flex-direction:column}
#header{padding:18px;background:#1e1e1e;font-weight:900;font-size:22px;letter-spacing:3px;color:#7c3aed;text-align:center}
.contact{padding:14px 16px;display:flex;gap:12px;cursor:pointer;border-bottom:1px solid #1e1e1e;align-items:center}
.contact:hover{background:#1a1a1a}
.active{background:#1e1e1e!important;border-left:4px solid #7c3aed}
.avatar{width:44px;height:44px;min-width:44px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#4f46e5);display:flex;align-items:center;justify-content:center;font-weight:bold}
#main{flex:1;display:flex;flex-direction:column;position:relative;background:#0a0a0a}
#top{padding:12px 16px;background:#1e1e1e;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #222}
#callIcons{display:flex;gap:18px;font-size:26px}
#callIcons span{cursor:pointer;padding:6px}
#msgs{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:10px;background:#0a0a0a}
.bubble{max-width:78%;padding:10px 14px;border-radius:18px;font-size:15px;line-height:1.4;word-wrap:break-word;position:relative}
.me{align-self:flex-end;background:#7c3aed;border-bottom-right-radius:4px}
.other{align-self:flex-start;background:#1e1e1e;border:1px solid #2a2a2a;border-bottom-left-radius:4px}
.ai{background:linear-gradient(135deg,#7c3aed,#4f46e5)!important;border:none!important}
.time{font-size:10px;opacity:.6;margin-left:8px;white-space:nowrap}
#inputArea{padding:10px 12px;background:#1e1e1e;display:flex;gap:10px;align-items:center;border-top:1px solid #222}
#inputArea input{flex:1;padding:13px 18px;border-radius:25px;border:none;background:#111;color:#fff;outline:none;font-size:15px}
.btn{width:42px;height:42px;min-width:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:20px;border:none;user-select:none}
.send{background:#7c3aed;color:#fff}
#videoBox{display:none;position:absolute;inset:0;background:#000;z-index:20;flex-direction:column}
#vids{flex:1;display:flex;flex-wrap:wrap;gap:10px;justify-content:center;align-items:center;padding:10px;overflow-y:auto}
video{width:320px;height:240px;background:#111;border-radius:16px;object-fit:cover;border:1px solid #222}
#vControls{padding:15px;background:#1e1e1e;display:flex;justify-content:center;gap:12px}
.vb{padding:12px 22px;border-radius:30px;border:none;font-weight:bold;cursor:pointer;background:#2a2a2a;color:#fff}
.end{background:#ef4444!important}
#recDot{display:none;color:#ef4444;font-size:12px;margin-left:8px;animation:blink 1s infinite}
@keyframes blink{0%{opacity:1}50%{opacity:0}}
</style></head><body>
<div id="sidebar">
<div id="header">TAMY</div>
<div id="contacts">
<div class="contact active" onclick="openChat('TAMY','T','ai')"><div class="avatar">T</div><div><b>TAMY</b><br><small style="color:#a78bfa">TAMY Intelligence</small></div></div>
<div class="contact" onclick="openChat('TAMY GROUP','G','group')"><div class="avatar" style="background:#222">G</div><div><b>TAMY GROUP</b><br><small id="gcount">Group • Live chat + calls</small></div></div>
</div>
<div id="live" style="padding:14px;font-size:12px;color:#666;border-top:1px solid #222;margin-top:auto">Connecting...</div>
</div>
<div id="main">
<div id="top"><div style="display:flex;gap:10px;align-items:center"><div class="avatar" id="hAv">T</div><div><b id="hName">TAMY</b><br><small id="hStat" style="color:#a78bfa">Online • TAMY Engine</small><span id="recDot">● REC</span></div></div>
<div id="callIcons"><span onclick="startCall(false)">📞</span><span onclick="startCall(true)">📹</span></div></div>
<div id="videoBox"><div id="vids"><video id="localV" autoplay muted playsinline></video><div id="remoteBox" style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center"></div></div>
<div id="vControls"><button class="vb" onclick="toggleMute()">🎙️ Mute</button><button class="vb" onclick="toggleCam()">📹 Cam</button><button class="vb end" onclick="endCall()">End Call</button></div></div>
<div id="msgs"></div>
<div id="inputArea">
<input id="inp" placeholder="Message TAMY..." onkeypress="if(event.key==='Enter')sendText()">
<button class="btn" style="background:#222" id="voiceBtn" onmousedown="startRec()" onmouseup="stopRec()" ontouchstart="startRec();event.preventDefault()" ontouchend="stopRec();event.preventDefault()">🎙️</button>
<button class="btn send" onclick="sendText()">➤</button>
</div>
</div>
<script>
let ws, mode='ai', pcs={}, localStream=null, recorder=null, chunks=[], isRec=false, muted=false, camOff=false;
const msgsEl=document.getElementById('msgs');

function openChat(name,av,m){
 mode=m; document.getElementById('hName').innerText=name; document.getElementById('hAv').innerText=av;
 document.querySelectorAll('.contact').forEach(c=>c.classList.remove('active')); if(event) event.currentTarget.classList.add('active');
 msgsEl.innerHTML='';
 if(m==='ai') addMsg('Welcome to TAMY 🚀<br><br>✓ Text chat with AI<br>✓ Hold 🎙️ for voice note<br>✓ Go to GROUP for calls<br><br>Tap TAMY GROUP on left for group chat, voice & video calls!','other ai');
 else addMsg('TAMY GROUP - Live! 🌍<br><br>Open this link in 2 tabs / 2 phones to test.<br>Text, voice notes, voice & video calls all work here.','other');
}

function getWsUrl(){ let proto = location.protocol==='https:'? 'wss:' : 'ws:'; return proto+'//'+location.host+'/ws/tamy'; }
function connect(){ ws=new WebSocket(getWsUrl());
 ws.onopen=()=>{ document.getElementById('live').innerText='Connected ✓'; };
 ws.onmessage=async e=>{ try{ let d=JSON.parse(e.data);
  if(d.type==='users'){ let list=d.users||[]; document.getElementById('live').innerHTML='Live ('+list.length+'):<br>'+list.join('<br>'); document.getElementById('gcount').innerText=list.length+' online • chat + calls'; }
  if(d.type==='chat'){ if(mode!=='ai') addMsg(d.text,'other'); }
  if(d.type==='signal'){ await handleSignal(d); }
 }catch(err){} };
 ws.onclose=()=>{ document.getElementById('live').innerText='Reconnecting...'; setTimeout(connect,2000); };
}
connect();

function addMsg(html,cls){
 let t=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
 let div=document.createElement('div'); div.className='bubble '+cls; div.innerHTML=html+`<span class="time"> ${t} ✓✓</span>`;
 msgsEl.appendChild(div); msgsEl.scrollTop=msgsEl.scrollHeight;
}

function sendText(){
 let input=document.getElementById('inp'); let text=input.value.trim(); if(!text) return;
 addMsg(text,'me'); input.value='';
 if(mode==='ai'){
  document.getElementById('hStat').innerText='TAMY typing...';
  fetch('/ai?message='+encodeURIComponent(text)).then(r=>r.json()).then(d=>{ addMsg(d.reply,'other ai'); document.getElementById('hStat').innerText='Online • TAMY Engine'; }).catch(()=>{ addMsg('TAMY is thinking... try again','other ai'); });
 } else {
  if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:text}));
 }
}

async function startRec(){
 if(isRec) return; try{
  let s=await navigator.mediaDevices.getUserMedia({audio:true});
  recorder=new MediaRecorder(s); chunks=[]; recorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); };
  recorder.onstop=()=>{ let blob=new Blob(chunks,{type:'audio/webm'}); let url=URL.createObjectURL(blob);
   addMsg(`<audio controls src="${url}"></audio><br>🎙️ Voice note`,'me');
   if(mode==='group' && ws && ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:'🎙️ Voice note'}));
   s.getTracks().forEach(t=>t.stop()); document.getElementById('recDot').style.display='none';
  };
  recorder.start(); isRec=true; document.getElementById('recDot').style.display='inline'; document.getElementById('voiceBtn').style.background='#ef4444';
 }catch(e){ alert('Mic permission needed!'); }
}
function stopRec(){ if(!isRec||!recorder) return; try{ recorder.stop(); }catch(e){} isRec=false; document.getElementById('voiceBtn').style.background='#222'; }

async function startCall(isVideo){
 if(mode==='ai'){ alert('Go to TAMY GROUP for voice/video calls! Click GROUP on left.'); return; }
 try{
  localStream=await navigator.mediaDevices.getUserMedia({video:isVideo,audio:true});
  document.getElementById('localV').srcObject=localStream;
  document.getElementById('videoBox').style.display='flex';
  if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'signal',data:{type:'call',isVideo:isVideo}}));
  addMsg(isVideo?'📹 Video call started... waiting for others':'📞 Voice call started... waiting for others','me');
 }catch(e){ alert('Camera/Mic permission needed!'); }
}
function createPC(id){
 let pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'},{urls:'stun:stun1.l.google.com:19302'}]});
 pc.onicecandidate=e=>{ if(e.candidate && ws && ws.readyState===1) ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate}})); };
 pc.ontrack=e=>{ let vidId='remote-'+id; let v=document.getElementById(vidId);
  if(!v){ v=document.createElement('video'); v.id=vidId; v.autoplay=true; v.playsInline=true; document.getElementById('remoteBox').appendChild(v); }
  v.srcObject=e.streams[0];
 };
 if(localStream) localStream.getTracks().forEach(t=>pc.addTrack(t,localStream));
 pcs[id]=pc; return pc;
}
async function handleSignal(d){
 let from=d.from||'peer'; let data=d.data||{};
 if(data.type==='call'){
  try{
   localStream=await navigator.mediaDevices.getUserMedia({video:data.isVideo,audio:true});
   document.getElementById('localV').srcObject=localStream;
   document.getElementById('videoBox').style.display='flex';
   let pc=createPC(from); let offer=await pc.createOffer(); await pc.setLocalDescription(offer);
   if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription}));
  }catch(e){}
 } else if(data.type==='offer'){
  let pc=createPC(from); await pc.setRemoteDescription(new RTCSessionDescription(data));
  let ans=await pc.createAnswer(); await pc.setLocalDescription(ans);
  if(ws && ws.readyState===1) ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription}));
 } else if(data.type==='answer'){
  let pc=pcs[from]; if(pc){ try{ await pc.setRemoteDescription(new RTCSessionDescription(data)); }catch(e){} }
 } else if(data.candidate){
  let pc=pcs[from]; if(pc){ try{ await pc.addIceCandidate(new RTCIceCandidate(data.candidate)); }catch(e){}
   else { for(let k in pcs){ try{ await pcs[k].addIceCandidate(new RTCIceCandidate(data.candidate)); }catch(e){} } }
  }
 }
}
function endCall(){
 document.getElementById('videoBox').style.display='none';
 if(localStream){ localStream.getTracks().forEach(t=>t.stop()); localStream=null; }
 for(let k in pcs){ try{ pcs[k].close(); }catch(e){} } pcs={};
 document.getElementById('remoteBox').innerHTML=''; document.getElementById('localV').srcObject=null;
 addMsg('Call ended','other');
}
function toggleMute(){ if(!localStream) return; muted=!muted; localStream.getAudioTracks().forEach(t=>t.enabled=!muted); }
function toggleCam(){ if(!localStream) return; camOff=!camOff; localStream.getVideoTracks().forEach(t=>t.enabled=!camOff); }

openChat('TAMY','T','ai');
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/ai")
def ai(message: str = ""):
    replies = [
        f"You said: '{message}'. I'm TAMY engine - I handle text, voice notes, voice calls & video calls all in one!",
        f"TAMY here! '{message}' - nice. Try TAMY GROUP for live group chat with your friends worldwide.",
        f"Got it: '{message}'. TAMY can do everything - chat, call, video. What do you want to build next?",
    ]
    import random
    return {"reply": random.choice(replies)}

@app.websocket("/ws/{room}")
async def ws_handler(websocket: WebSocket, room: str):
    await websocket.accept()
    cid = str(id(websocket))
    clients[cid] = websocket
    await broadcast_users()
    try:
        while True:
            data = await websocket.receive_text()
            # broadcast to others
            for other_id, other_ws in list(clients.items()):
                if other_id!= cid:
                    try:
                        # add from id so clients know who sent
                        msg = json.loads(data)
                        msg['from'] = cid
                        await other_ws.send_text(json.dumps(msg))
                    except:
                        try: await other_ws.send_text(data)
                        except: pass
    except WebSocketDisconnect:
        pass
    finally:
        if cid in clients: del clients[cid]
        await broadcast_users()

async def broadcast_users():
    users = [f"User{str(id(c))[-4:]}" for c in clients.values()]
    payload = json.dumps({"type": "users", "users": users})
    for ws in list(clients.values()):
        try: await ws.send_text(payload)
        except: pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
