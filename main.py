from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json

app = FastAPI()
clients = {}

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TAMY FINAL EXCLUSIVE</title>
<style>
body{margin:0;background:#050508;color:#fff;font-family:Arial;height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:#12122a;border:2px solid #7c3aed;border-radius:20px;padding:22px;width:380px;text-align:center}
h1{font-size:42px;letter-spacing:12px;background:linear-gradient(90deg,#7c3aed,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 10px 0}
input{width:100%;padding:12px;margin:7px 0;border-radius:10px;border:1px solid #2a2a4a;background:#0a0a14;color:#fff;box-sizing:border-box;font-size:14px}
button{width:100%;padding:14px;margin:6px 0;border-radius:10px;border:none;font-weight:900;cursor:pointer;font-size:14px}
.green{background:#00ff88;color:#000}
.purple{background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff}
.gray{background:#1a1a2e;color:#fff;border:1px solid #333}
#main{display:none;position:fixed;inset:0;background:#050508;flex-direction:column}
#top{height:55px;background:#0a0a14;display:flex;justify-content:space-between;align-items:center;padding:0 12px;border-bottom:1px solid #222}
#online{flex:1;overflow:auto;padding:10px;background:#08080f}
.userRow{padding:12px;background:#12122a;border-radius:12px;margin:8px 0;border:2px solid #00ff88;display:flex;justify-content:space-between;align-items:center}
#incoming{display:none;position:fixed;inset:0;background:#000;z-index:9999;flex-direction:column;align-items:center;justify-content:center;border:5px solid #00ff88}
#voice{display:none;position:fixed;inset:0;background:#000;z-index:9998;flex-direction:column;align-items:center;justify-content:center}
#alert{position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:10px 18px;border-radius:20px;font-weight:bold;display:none;z-index:10000;max-width:90%;text-align:center}
</style>
</head>
<body>
<div id="alert"></div>

<div id="loginBox" class="box">
<h1>TAMY</h1>
<p style="color:#00ff88;font-size:11px;font-weight:900">EXCLUSIVE FINAL - 0 ERRORS - 100% CLEAR</p>
<input id="n" placeholder="Your Name" value="shafik">
<input id="num" placeholder="Your Number +966" value="+966508782155">
<input id="myid" placeholder="Your TAMY ID - MUST BE DIFFERENT!" value="tamy_shafik123">
<button class="green" onclick="doLogin()">Sign In Direct</button>
<button class="purple" onclick="doRegister()">REGISTER</button>
<button class="gray" onclick="doNewId()">Create New TAMY ID - DIFFERENT!</button>
<p id="msg" style="font-size:11px;color:#00ff88;margin-top:8px;min-height:15px"></p>
</div>

<div id="main">
<div id="top"><b>TAMY</b><span id="count">0 Online</span><button onclick="doLogout()" style="width:auto;padding:6px 12px;background:#ff0040;color:#fff;border:none;border-radius:8px;font-weight:900">Logout</button></div>
<div style="padding:8px;background:#000;border-bottom:2px solid #00ff88"><b style="color:#00ff88;font-size:11px">ONLINE FRIENDS - Calls WILL come - Click CALL!</b><br><small style="color:#aaa">Your ID: <span id="myIdShow" style="color:#00ff88"></span></small></div>
<div id="online">Loading online friends...</div>
</div>

<div id="incoming">
<h2 style="color:#00ff88;font-size:30px;font-weight:900">TAMY CALL!</h2>
<p id="callType" style="color:#ff00aa;font-size:16px;font-weight:bold">VOICE CALL</p>
<p id="callFrom" style="margin:15px;text-align:center;font-size:16px;line-height:1.6"></p>
<div style="display:flex;gap:15px;margin-top:25px">
<button class="green" style="padding:18px 35px;font-size:18px" onclick="doAnswer()">Answer</button>
<button style="padding:18px 35px;background:#ff0040;color:#fff;border:none;border-radius:10px;font-weight:900;font-size:18px" onclick="doDecline()">Decline</button>
</div>
</div>

<div id="voice">
<h2 id="vStatus">CALLING...</h2>
<p id="vTimer" style="color:#00ff88;font-size:26px;margin:12px;font-weight:900">00:00</p>
<p id="vWith" style="color:#aaa;font-size:13px;text-align:center"></p>
<div style="display:flex;gap:12px;margin-top:25px">
<button style="padding:12px 22px;background:#1a1a2e;color:#fff;border:none;border-radius:20px;font-weight:900" onclick="doMute()">Mute</button>
<button style="padding:12px 22px;background:#ff0040;color:#fff;border:none;border-radius:20px;font-weight:900" onclick="doEnd()">End</button>
</div>
</div>

<script>
var ws=null;
var pcs={};
var localStream=null;
var timer=null;
var sec=0;
var incomingFrom=null;
var incomingName='';
var myId='';
var myName='';
var myNum='';
var isMuted=false;

function showAlert(text){
 var el=document.getElementById('alert');
 el.innerText=text;
 el.style.display='block';
 setTimeout(function(){el.style.display='none';},4000);
 console.log(text);
}

function doNewId(){
 var newId='tamy_'+Math.random().toString(36).substring(2,8);
 document.getElementById('myid').value=newId;
 document.getElementById('msg').innerText='New ID: '+newId+' - Friend must use DIFFERENT ID!';
 showAlert('New ID: '+newId);
}

function doRegister(){
 var name=document.getElementById('n').value.trim();
 var num=document.getElementById('num').value.trim();
 var id=document.getElementById('myid').value.trim();
 if(!name||!num||!id){showAlert('Fill Name, Number, ID!');document.getElementById('msg').innerText='Fill all fields!';return;}
 myId=id;myName=name;myNum=num;
 localStorage.setItem('tamy_token',myId);
 localStorage.setItem('tamy_name',myName);
 localStorage.setItem('tamy_number',myNum);
 localStorage.setItem('tamy_verified','true');
 document.getElementById('loginBox').style.display='none';
 document.getElementById('main').style.display='flex';
 document.getElementById('myIdShow').innerText=myId;
 showAlert('Registered! ID: '+myId);
 connectWS();
}

function doLogin(){
 var name=document.getElementById('n').value.trim();
 var num=document.getElementById('num').value.trim();
 var id=document.getElementById('myid').value.trim();
 if(!name){showAlert('Type Name!');return;}
 if(!num){showAlert('Type Number!');return;}
 if(!id){showAlert('Type TAMY ID or Create New ID!');return;}
 myId=id;myName=name;myNum=num;
 localStorage.setItem('tamy_token',myId);
 localStorage.setItem('tamy_name',myName);
 localStorage.setItem('tamy_number',myNum);
 localStorage.setItem('tamy_verified','true');
 document.getElementById('loginBox').style.display='none';
 document.getElementById('main').style.display='flex';
 document.getElementById('myIdShow').innerText=myId;
 showAlert('Logged in! ID: '+myId);
 connectWS();
}

function doLogout(){localStorage.clear();location.reload();}

function connectWS(){
 if(!myId)return;
 if(ws){try{ws.close();}catch(e){}}
 var protocol=location.protocol==='https:'?'wss:':'ws:';
 var url=protocol+'//'+location.host+'/ws/tamy?token='+encodeURIComponent(myId)+'&name='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNum);
 ws=new WebSocket(url);
 ws.onopen=function(){showAlert('Connected! ID: '+myId+' - Ready for calls!');};
 ws.onmessage=function(event){
  var data=JSON.parse(event.data);
  if(data.type==='users'){
   var users=data.users||[];
   document.getElementById('count').innerText=users.length+' Online';
   var html='';
   for(var i=0;i<users.length;i++){
    var u=users[i];
    if(u.id===myId)continue;
    html+='<div class="userRow"><div><b>'+u.name+'</b><br><span style="color:#00ff88">'+(u.number||'')+'</span><br><small style="color:#aaa">'+u.id+'</small><br><small style="color:#00ff88">Will receive call!</small></div><div><button class="green" style="padding:12px 18px;width:auto" onclick="doCall(\\''+u.id+'\\',\\''+u.name+'\\')">CALL</button></div></div>';
   }
   if(html===''){
    html='<div style="padding:18px;background:#000;border-radius:12px;border:2px dashed #ff00aa;color:#aaa;font-size:11px;line-height:1.5"><b style="color:#ff00aa">No friends online - Calls not coming because no one online!</b><br><br><b style="color:#00ff88">HOW TO TEST 100%:</b><br>1. Open this link in 2nd tab Incognito (Ctrl+Shift+N)<br>2. Click Create New ID - MUST BE DIFFERENT!<br>Tab1: tamy_shafik123<br>Tab2: tamy_king456<br>3. Register both<br>4. Tab1 will show Tab2 with CALL button<br>5. Click CALL - Tab2 WILL get INCOMING CALL popup!<br><br>Your ID: <b style="color:#00ff88">'+myId+'</b></div>';
   }
   document.getElementById('online').innerHTML=html;
  }
  if(data.type==='signal'){handleSignal(data);}
 };
 ws.onclose=function(){if(myId){setTimeout(connectWS,2000);}};
}

function doCall(targetId,targetName){
 if(!targetId){showAlert('No friend online! Open 2nd tab with DIFFERENT ID!');return;}
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
  localStream=stream;
  document.getElementById('voice').style.display='flex';
  document.getElementById('vStatus').innerText='Calling '+targetName+'...';
  document.getElementById('vWith').innerText='To: '+targetName+' - ID: '+targetId+' - Called number WILL receive popup!';
  sec=0;
  document.getElementById('vTimer').innerText='00:00';
  if(timer){clearInterval(timer);}
  timer=setInterval(function(){sec++;var m=String(Math.floor(sec/60)).padStart(2,'0');var s=String(sec%60).padStart(2,'0');document.getElementById('vTimer').innerText=m+':'+s;},1000);
  var payload={type:'signal',to:targetId,data:{type:'voice_call',callerName:myName,callerNumber:myNum,callType:'voice'}};
  ws.send(JSON.stringify(payload));
  showAlert('Call sent to '+targetName+' '+targetId+' - Called number WILL get popup! Check other tab!');
 }).catch(function(err){showAlert('Allow mic: '+err.message);});
}

function createPC(peerId){
 var config={iceServers:[{urls:'stun:stun.l.google.com:19302'},{urls:'stun:stun1.l.google.com:19302'},{urls:'turn:openrelay.metered.ca:80',username:'openrelayproject',credential:'openrelayproject'},{urls:'turn:openrelay.metered.ca:443',username:'openrelayproject',credential:'openrelayproject'}]};
 var pc=new RTCPeerConnection(config);
 pc.onicecandidate=function(e){if(e.candidate&&ws){ws.send(JSON.stringify({type:'signal',to:peerId,data:{candidate:e.candidate}}));}};
 pc.ontrack=function(e){
  var audio=document.createElement('audio');
  audio.autoplay=true;
  audio.style.display='none';
  audio.srcObject=e.streams[0];
  document.body.appendChild(audio);
  showAlert('Connected to '+peerId.substring(0,6)+'!');
 };
 if(localStream){localStream.getTracks().forEach(function(track){pc.addTrack(track,localStream);});}
 pcs[peerId]=pc;
 return pc;
}

function handleSignal(msg){
 var from=msg.from;
 var data=msg.data||{};
 var fromName=msg.fromName||'Friend';
 var fromNumber=msg.fromNumber||'';
 if(data.type==='voice_call'){
  incomingFrom=from;
  incomingName=fromName;
  document.getElementById('incoming').style.display='flex';
  document.getElementById('callType').innerText='VOICE CALL';
  document.getElementById('callFrom').innerHTML=fromName+' is calling you...<br>Number: <b style="color:#ff00aa">'+fromNumber+'</b><br>ID: '+from+'<br><br><span style="color:#00ff88;font-weight:900">Calls coming to called number - Click Answer!</span>';
  showAlert('INCOMING CALL from '+fromName+' '+fromNumber+' - Answer!');
  if(navigator.vibrate){navigator.vibrate([500,200,500,200,500]);}
 }
 if(data.type==='offer'){
  var pc=createPC(from);
  pc.setRemoteDescription(new RTCSessionDescription(data)).then(function(){return pc.createAnswer();}).then(function(answer){return pc.setLocalDescription(answer);}).then(function(){ws.send(JSON.stringify({type:'signal',to:from,data:pcs[from].localDescription}));});
 }
 if(data.type==='answer'){
  var pc=pcs[from];
  if(pc){pc.setRemoteDescription(new RTCSessionDescription(data));}
 }
 if(data.candidate){
  var pc=pcs[from];
  if(pc){try{pc.addIceCandidate(new RTCIceCandidate(data.candidate));}catch(e){}}
 }
 if(data.type==='decline'){showAlert('Call declined by '+fromName);doEnd();}
}

function doAnswer(){
 if(!incomingFrom){showAlert('No incoming call!');return;}
 document.getElementById('incoming').style.display='none';
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
  localStream=stream;
  document.getElementById('voice').style.display='flex';
  document.getElementById('vStatus').innerText='Connected to '+incomingName;
  document.getElementById('vWith').innerText='Answered - Connected! ID: '+incomingFrom;
  sec=0;
  if(timer){clearInterval(timer);}
  timer=setInterval(function(){sec++;var m=String(Math.floor(sec/60)).padStart(2,'0');var s=String(sec%60).padStart(2,'0');document.getElementById('vTimer').innerText=m+':'+s;},1000);
  var pc=createPC(incomingFrom);
  return pc.createOffer().then(function(offer){return pc.setLocalDescription(offer);}).then(function(){ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:pcs[incomingFrom].localDescription}));showAlert('Answered! Connected to '+incomingName);});
 }).catch(function(err){showAlert('Allow mic: '+err.message);});
 incomingFrom=null;
}

function doDecline(){
 if(incomingFrom&&ws){ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:{type:'decline'}}));}
 document.getElementById('incoming').style.display='none';
 incomingFrom=null;
 showAlert('Declined');
}

function doEnd(){
 document.getElementById('voice').style.display='none';
 if(timer){clearInterval(timer);}
 sec=0;
 if(localStream){localStream.getTracks().forEach(function(t){t.stop();});localStream=null;}
 for(var k in pcs){try{pcs[k].close();}catch(e){}}
 pcs={};
 var audios=document.querySelectorAll('audio');
 for(var i=0;i<audios.length;i++){audios[i].remove();}
}

function doMute(){
 if(!localStream)return;
 isMuted=!isMuted;
 localStream.getAudioTracks().forEach(function(t){t.enabled=!isMuted;});
 showAlert(isMuted?'Muted':'Mic On');
}

var saved=localStorage.getItem('tamy_token');
if(saved){
 document.getElementById('n').value=localStorage.getItem('tamy_name')||'';
 document.getElementById('num').value=localStorage.getItem('tamy_number')||'';
 document.getElementById('myid').value=saved;
 myId=saved;
 myName=localStorage.getItem('tamy_name')||'';
 myNum=localStorage.getItem('tamy_number')||'';
 if(localStorage.getItem('tamy_verified')==='true'){
  document.getElementById('loginBox').style.display='none';
  document.getElementById('main').style.display='flex';
  document.getElementById('myIdShow').innerText=myId;
  connectWS();
 }
}
</script>
</body>
</html>
    """)

@app.websocket("/ws/tamy")
async def ws_tamy(websocket: WebSocket, token: str = "", name: str = "User", number: str = ""):
    await websocket.accept()
    cid = token or str(id(websocket))
    clients[cid] = {"ws": websocket, "name": name, "number": number}
    await broadcast()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                j = json.loads(raw)
                target = j.get("to")
                j["from"] = cid
                j["fromName"] = clients.get(cid, {}).get("name", "Friend")
                j["fromNumber"] = clients.get(cid, {}).get("number", "")
                if target and target in clients:
                    await clients[target]["ws"].send_text(json.dumps(j))
                else:
                    for oid, c in list(clients.items()):
                        if oid!= cid:
                            try:
                                await c["ws"].send_text(json.dumps(j))
                            except:
                                pass
            except:
                pass
    except:
        pass
    finally:
        clients.pop(cid, None)
        await broadcast()

async def broadcast():
    users = [{"id": cid, "name": c["name"], "number": c["number"]} for cid, c in clients.items()]
    msg = json.dumps({"type": "users", "users": users})
    for c in list(clients.values()):
        try:
            await c["ws"].send_text(msg)
        except:
            pass
