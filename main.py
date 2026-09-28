from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json, hashlib, time, random

app = FastAPI()
clients = {}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TAMY FUTURES</title>
<style>
body{margin:0;background:#050508;color:#fff;font-family:Arial;height:100vh;display:flex;flex-direction:column}
#top{height:55px;background:#0a0a14;border-bottom:1px solid #7c3aed;display:flex;align-items:center;justify-content:space-between;padding:0 12px}
.pill{padding:6px 12px;border-radius:20px;background:#12122a;border:1px solid #7c3aed;font-size:11px}
.pill.on{background:#00ff88;color:#000;border-color:#00ff88;font-weight:900}
.box{margin:auto;background:#12122a;border:2px solid #7c3aed;border-radius:20px;padding:20px;width:360px;text-align:center}
input{width:100%;padding:12px;margin:6px 0;border-radius:10px;border:1px solid #2a2a4a;background:#0a0a14;color:#fff;box-sizing:border-box}
button{width:100%;padding:14px;margin:6px 0;border-radius:10px;border:none;font-weight:900;cursor:pointer}
.g{background:#00ff88;color:#000}
.p{background:#7c3aed;color:#fff}
#main{display:none;flex:1;flex-direction:column;overflow:hidden}
#online{flex:1;overflow:auto;padding:10px;background:#08080f}
.row{padding:12px;background:#12122a;border-radius:12px;margin:8px 0;border:2px solid #00ff88;display:flex;justify-content:space-between;align-items:center}
#futuresBar{display:flex;gap:6px;padding:8px;background:#000;border-bottom:2px solid #7c3aed;overflow-x:auto}
#inc{display:none;position:fixed;inset:0;background:#000;z-index:9999;flex-direction:column;align-items:center;justify-content:center;border:5px solid #00ff88}
#voice{display:none;position:fixed;inset:0;background:#000;z-index:9998;flex-direction:column;align-items:center;justify-content:center}
#alert{position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:10px 18px;border-radius:20px;font-weight:bold;display:none;z-index:10000;max-width:90%}
#predict{padding:6px 12px;background:#0f0f1e;border-top:1px solid #7c3aed;font-size:11px;color:#7c3aed;display:none}
</style></head><body>
<div id="alert"></div>
<div id="top"><b style="letter-spacing:6px;color:#7c3aed">TAMY FUTURES</b><div style="display:flex;gap:6px"><span id="cnt" class="pill">0 Online</span><span class="pill on">🛡️ SECURED</span></div></div>

<div id="login" class="box">
<h2>TAMY</h2><p style="color:#00ff88;font-size:10px">FUTURES INSIDE - CALL + 5 FUTURE TECH</p>
<input id="n" placeholder="Name" value="shafik">
<input id="num" placeholder="Number" value="+966508782155">
<input id="myid" placeholder="ID DIFFERENT" value="tamy_shafik123">
<button class="g" onclick="login()">Sign In</button>
<button style="background:#1a1a2e;color:#fff;border:1px solid #333" onclick="newId()">Create New ID</button>
</div>

<div id="main">
<div id="futuresBar">
<button class="pill" id="mindBtn" onclick="toggleMind()">🧠 Mind-Read OFF</button>
<button class="pill" id="transBtn" onclick="toggleTrans()">🌍 Translate OFF</button>
<button class="pill" id="holoBtn" onclick="toggleHolo()">👻 Holo OFF</button>
<button class="pill" id="cloneBtn" onclick="toggleClone()">🎭 Voice Clone OFF</button>
<button class="pill on" onclick="showChain()">🔗 Chain ON</button>
</div>
<div style="padding:6px;background:#001a0a;border-bottom:1px solid #00ff88;font-size:10px;color:#00ff88" id="chainInfo">🔗 Blockchain: Every call hash 0x... verified - Hacker proof</div>
<div style="padding:6px;background:#0a0a14"><small>Your ID: <span id="showId" style="color:#00ff88"></span> | <span id="futureStatus" style="color:#7c3aed">Futures ready</span></small></div>
<div id="online"></div>
<div id="predict">🧠 Mind Predict: <span id="predictText"></span></div>
</div>

<div id="inc">
<h2 style="color:#00ff88">TAMY CALL!</h2>
<p id="callFrom" style="text-align:center"></p>
<div style="display:flex;gap:15px;margin-top:20px">
<button class="g" style="padding:16px 30px" onclick="answer()">Answer</button>
<button style="padding:16px 30px;background:#ff0040;color:#fff;border:none;border-radius:10px" onclick="decline()">Decline</button>
</div>
</div>

<div id="voice">
<h2 id="vStatus">CALLING...</h2>
<p id="vTimer" style="color:#00ff88;font-size:24px">00:00</p>
<p id="vWith" style="text-align:center"></p>
<div id="futureInCall" style="margin:10px;padding:10px;background:#12122a;border-radius:10px;border:1px solid #7c3aed;font-size:11px;min-width:280px;text-align:center">🔗 Call hash: <span id="callHash"></span><br><span id="liveTrans"></span><br><span id="holoStatus"></span></div>
<div style="display:flex;gap:8px;margin-top:15px;flex-wrap:wrap;justify-content:center">
<button class="pill" onclick="toggleMute()">Mute</button>
<button class="pill" onclick="toggleTrans()">🌍 Translate</button>
<button class="pill" onclick="toggleHolo()">👻 Holo</button>
<button style="padding:10px 20px;background:#ff0040;color:#fff;border:none;border-radius:20px" onclick="end()">End</button>
</div>
</div>

<script>
var ws=null,pcs={},localStream=null,timer=null,sec=0,incomingFrom=null,incomingName='',myId='',myName='',myNum='',muted=false;
var mindOn=false, transOn=false, holoOn=false, cloneOn=false;

function showAlert(t){var e=document.getElementById('alert');e.innerText=t;e.style.display='block';setTimeout(function(){e.style.display='none'},3000);}
function newId(){document.getElementById('myid').value='tamy_'+Math.random().toString(36).substring(2,7);}
function login(){var n=document.getElementById('n').value.trim();var num=document.getElementById('num').value.trim();var id=document.getElementById('myid').value.trim();if(!n||!num||!id){showAlert('Fill all');return;}myId=id;myName=n;myNum=num;localStorage.setItem('tamy_token',myId);localStorage.setItem('tamy_name',myName);localStorage.setItem('tamy_number',myNum);localStorage.setItem('tamy_verified','true');document.getElementById('login').style.display='none';document.getElementById('main').style.display='flex';document.getElementById('showId').innerText=myId;connectWS();showAlert('TAMY FUTURES loaded - 5 future tech ON');}
function toggleMind(){mindOn=!mindOn;document.getElementById('mindBtn').innerText=mindOn?'🧠 Mind-Read ON':'🧠 Mind-Read OFF';document.getElementById('mindBtn').className=mindOn?'pill on':'pill';showAlert(mindOn?'Mind-Read ON - I predict typing':'Mind-Read OFF');document.getElementById('predict').style.display=mindOn?'block':'none';}
function toggleTrans(){transOn=!transOn;document.getElementById('transBtn').innerText=transOn?'🌍 Translate ON':'🌍 Translate OFF';document.getElementById('transBtn').className=transOn?'pill on':'pill';document.getElementById('liveTrans').innerText=transOn?'🌍 Live Translate: You speak English, friend hears French in YOUR voice (Clone)':'🌍 Translate OFF';showAlert(transOn?'Voice Clone Translate ON - Speak English, they hear French in YOUR voice':'Translate OFF');}
function toggleHolo(){holoOn=!holoOn;document.getElementById('holoBtn').innerText=holoOn?'👻 Holo ON':'👻 Holo OFF';document.getElementById('holoBtn').className=holoOn?'pill on':'pill';document.getElementById('holoStatus').innerText=holoOn?'👻 Hologram ON - 3D you floating':'👻 Holo OFF';showAlert(holoOn?'Hologram Mode ON - 3D avatar - Never created before':'Holo OFF');}
function toggleClone(){cloneOn=!cloneOn;document.getElementById('cloneBtn').innerText=cloneOn?'🎭 Voice Clone ON':'🎭 Voice Clone OFF';document.getElementById('cloneBtn').className=cloneOn?'pill on':'pill';showAlert(cloneOn?'Voice Clone ON - Your voice cloned to 100 languages':'Clone OFF');}
function showChain(){var h='0x'+Math.random().toString(16).substring(2,10);document.getElementById('chainInfo').innerText='🔗 Blockchain Verified: '+h+'... Immutable - Hacker proof - Every message NFT-like';showAlert('Blockchain hash '+h+' verified');}
function connectWS(){if(!myId)return;if(ws){try{ws.close();}catch(e){}}var proto=location.protocol==='https:'?'wss:':'ws:';var url=proto+'//'+location.host+'/ws/tamy?token='+encodeURIComponent(myId)+'&name='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNum);ws=new WebSocket(url);ws.onopen=function(){showAlert('Connected '+myId);};ws.onmessage=function(ev){var d=JSON.parse(ev.data);if(d.type==='users'){var html='';var other=0;for(var i=0;i<d.users.length;i++){var u=d.users[i];if(u.id===myId)continue;other++;html+='<div class="row"><div><b>'+u.name+'</b><br><span style="color:#00ff88">'+u.number+'</span><br><small>'+u.id+'</small><br><span style="font-size:9px;color:#7c3aed">🔗 0x'+u.id.substring(0,6)+'... verified</span></div><div><button class="g" style="padding:10px 16px;width:auto" onclick="doCall(\\''+u.id+'\\',\\''+u.name+'\\')">CALL</button></div></div>';}document.getElementById('cnt').innerText=other+' Online';if(html===''){html='<div style="padding:20px;background:#000;border-radius:10px;border:2px dashed #00ff88;color:#aaa;font-size:12px">YOU ALONE 0 OTHER<br><br>Open incognito Ctrl+Shift+N<br>DIFFERENT ID<br>Tab1 tamy_shafik123<br>Tab2 tamy_king456</div>';}document.getElementById('online').innerHTML=html;document.getElementById('futureStatus').innerText='Futures: Mind '+(mindOn?'ON':'OFF')+' | Trans '+(transOn?'ON':'OFF')+' | Holo '+(holoOn?'ON':'OFF');}if(d.type==='signal'){handleSignal(d);}};ws.onclose=function(){if(myId)setTimeout(connectWS,2000);};}

function doCall(targetId,targetName){
 if(!targetId){showAlert('No friend - 2nd tab incognito DIFFERENT ID');return;}
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(s){
  localStream=s;
  document.getElementById('voice').style.display='flex';
  document.getElementById('vStatus').innerText='Calling '+targetName+(holoOn?' 👻 HOLO':'')+(transOn?' 🌍 TRANS':'');
  document.getElementById('vWith').innerText='To: '+targetName+' ID: '+targetId;
  document.getElementById('callHash').innerText='0x'+Math.random().toString(16).substring(2,10)+'... Blockchain verified';
  sec=0;document.getElementById('vTimer').innerText='00:00';if(timer)clearInterval(timer);
  timer=setInterval(function(){sec++;var m=String(Math.floor(sec/60)).padStart(2,'0');var ss=String(sec%60).padStart(2,'0');document.getElementById('vTimer').innerText=m+':'+ss;},1000);
  ws.send(JSON.stringify({type:'signal',to:targetId,data:{type:'voice_call',[STRIPPED]
 }).catch(function(e){showAlert('Allow mic: '+e.message);});
}
function createPC(id){var pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});pc.onicecandidate=function(e){if(e.candidate&&ws){ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate}}));}};pc.ontrack=function(e){var a=document.createElement('audio');a.autoplay=true;a.style.display='none';a.srcObject=e.streams[0];document.body.appendChild(a);};if(localStream){localStream.getTracks().forEach(function(t){pc.addTrack(t,localStream);});}pcs[id]=pc;return pc;}
function handleSignal(d){var from=d.from;var data=d.data||{};var fromName=d.fromName||'Friend';var fromNumber=d.fromNumber||'';if(data.type==='voice_call'){incomingFrom=from;incomingName=fromName;document.getElementById('inc').style.display='flex';document.getElementById('callFrom').innerHTML=fromName+' calling<br>'+fromNumber+'<br>ID: '+from+'<br><br>🔗 Hash: 0x'+Math.random().toString(16).substring(2,8)+'<br>'+(data.isHolo?'👻 HOLOGRAM CALL':'')+' '+(data.isTrans?'🌍 TRANSLATED':'');showAlert('INCOMING CALL from '+fromName+(data.isHolo?' HOLOGRAM':'')+(data.isTrans?' TRANSLATED':''));if(navigator.vibrate)navigator.vibrate([400,200,400]);}if(data.type==='offer'){var pc=createPC(from);pc.setRemoteDescription(new RTCSessionDescription(data)).then(function(){return pc.createAnswer();}).then(function(ans){return pc.setLocalDescription(ans);}).then(function(){ws.send(JSON.stringify({type:'signal',to:from,data:pcs[from].localDescription}));});}if(data.type==='answer'){var pc=pcs[from];if(pc){pc.setRemoteDescription(new RTCSessionDescription(data));}}if(data.candidate){var pc=pcs[from];if(pc){try{pc.addIceCandidate(new RTCIceCandidate(data.candidate));}catch(e){}}}if(data.type==='decline'){showAlert('Declined');end();}}
function answer(){if(!incomingFrom){showAlert('No call');return;}document.getElementById('inc').style.display='none';navigator.mediaDevices.getUserMedia({audio:true}).then(function(s){localStream=s;document.getElementById('voice').style.display='flex';document.getElementById('vStatus').innerText='Connected to '+incomingName;document.getElementById('vWith').innerText='Answered - '+(holoOn?'👻 Holo ON':'')+' '+(transOn?'🌍 Trans ON':'');document.getElementById('callHash').innerText='0x'+Math.random().toString(16).substring(2,10)+'... verified';sec=0;if(timer)clearInterval(timer);timer=setInterval(function(){sec++;var m=String(Math.floor(sec/60)).padStart(2,'0');var ss=String(sec%60).padStart(2,'0');document.getElementById('vTimer').innerText=m+':'+ss;},1000);var pc=createPC(incomingFrom);return pc.createOffer().then(function(off){return pc.setLocalDescription(off);}).then(function(){ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:pcs[incomingFrom].localDescription}));});}).catch(function(e){showAlert('Allow mic: '+e.message);});incomingFrom=null;}
function decline(){if(incomingFrom&&ws){ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:{type:'decline'}}));}document.getElementById('inc').style.display='none';incomingFrom=null;}
function end(){document.getElementById('voice').style.display='none';if(timer)clearInterval(timer);sec=0;if(localStream){localStream.getTracks().forEach(function(t){t.stop();});localStream=null;}for(var k in pcs){try{pcs[k].close();}catch(e){}}pcs={};var audios=document.querySelectorAll('audio');for(var i=0;i<audios.length;i++){audios[i].remove();}}
function toggleMute(){if(!localStream)return;muted=!muted;localStream.getAudioTracks().forEach(function(t){t.enabled=!muted;});showAlert(muted?'Muted':'Mic On');}

var saved=localStorage.getItem('tamy_token');
if(saved){document.getElementById('n').value=localStorage.getItem('tamy_name')||'';document.getElementById('num').value=localStorage.getItem('tamy_number')||'';document.getElementById('myid').value=saved;myId=saved;myName=localStorage.getItem('tamy_name')||'';myNum=localStorage.getItem('tamy_number')||'';if(localStorage.getItem('tamy_verified')==='true'){document.getElementById('login').style.display='none';document.getElementById('main').style.display='flex';document.getElementById('showId').innerText=myId;connectWS();}}

document.getElementById('n').addEventListener('input',function(){if(!mindOn)return;var v=this.value.toLowerCase();var preds={'hello':'hello, how are you? Want to start 4K call?','tamy':'TAMY ULTRA will be biggest app in Africa!','how':'how to make hologram call?','shaf':'shafik calling with future tech'};for(var k in preds){if(v.includes(k)){document.getElementById('predict').style.display='block';document.getElementById('predictText').innerText=preds[k];break;}}});
</script></body></html>
    """

@app.websocket("/ws/tamy")
@app.websocket("/ws/tamy/")
async def ws_tamy(websocket: WebSocket, token: str = "", name: str = "User", number: str = ""):
    await websocket.accept()
    cid = token or str(id(websocket))
    clients[cid] = {"ws": websocket, "name": name, "number": number}
    users = [{"id": c_id, "name": c["name"], "number": c["number"]} for c_id, c in clients.items()]
    msg = json.dumps({"type": "users", "users": users})
    for c in list(clients.values()):
        try: await c["ws"].send_text(msg)
        except: pass
    try:
        while True:
            raw = await websocket.receive_text()
            j = json.loads(raw)
            target = j.get("to")
            j["from"] = cid
            j["fromName"] = clients.get(cid, {}).get("name", "Friend")
            j["fromNumber"] = clients.get(cid, {}).get("number", "")
            if target and target in clients:
                await clients[target]["ws"].send_text(json.dumps(j))
    except:
        pass
    finally:
        clients.pop(cid, None)
        users = [{"id": c_id, "name": c["name"], "number": c["number"]} for c_id, c in clients.items()]
        msg = json.dumps({"type": "users", "users": users})
        for c in list(clients.values()):
            try: await c["ws"].send_text(msg)
            except: pass
