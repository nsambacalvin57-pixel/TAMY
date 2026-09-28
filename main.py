from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()
clients = {}

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TAMY FINAL WORKING</title>
<style>
body{margin:0;background:#050508;color:#fff;font-family:Arial;height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:#12122a;border:2px solid #7c3aed;border-radius:20px;padding:22px;width:380px;text-align:center}
h1{font-size:42px;letter-spacing:12px;background:linear-gradient(90deg,#7c3aed,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0}
input{width:100%;padding:12px;margin:7px 0;border-radius:10px;border:1px solid #2a2a4a;background:#0a0a14;color:#fff;box-sizing:border-box}
button{width:100%;padding:14px;margin:6px 0;border-radius:10px;border:none;font-weight:900;cursor:pointer}
.green{background:#00ff88;color:#000}
.purple{background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff}
.gray{background:#1a1a2e;color:#fff;border:1px solid #333}
#main{display:none;position:fixed;inset:0;background:#050508;flex-direction:column}
#top{height:55px;background:#0a0a14;display:flex;justify-content:space-between;align-items:center;padding:0 12px;border-bottom:1px solid #222}
#online{flex:1;overflow:auto;padding:10px;background:#08080f}
.userRow{padding:14px;background:#12122a;border-radius:12px;margin:10px 0;border:2px solid #00ff88;display:flex;justify-content:space-between;align-items:center}
#incoming{display:none;position:fixed;inset:0;background:#000;z-index:9999;flex-direction:column;align-items:center;justify-content:center;border:5px solid #00ff88}
#voice{display:none;position:fixed;inset:0;background:#000;z-index:9998;flex-direction:column;align-items:center;justify-content:center}
#alert{position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:10px 18px;border-radius:20px;font-weight:bold;display:none;z-index:10000;max-width:90%;text-align:center}
</style></head><body>
<div id="alert"></div>
<div id="loginBox" class="box">
<h1>TAMY</h1>
<p style="color:#00ff88;font-size:11px;font-weight:900">FINAL WORKING - 0 ONLINE FIXED</p>
<input id="n" placeholder="Your Name" value="shafik">
<input id="num" placeholder="Number +966" value="+966508782155">
<input id="myid" placeholder="TAMY ID MUST BE DIFFERENT!" value="tamy_shafik123">
<button class="green" onclick="doLogin()">Sign In Direct</button>
<button class="purple" onclick="doRegister()">REGISTER</button>
<button class="gray" onclick="doNewId()">Create New TAMY ID</button>
<p id="msg" style="font-size:11px;color:#00ff88"></p>
</div>
<div id="main">
<div id="top"><b>TAMY</b><span id="count">0 Online</span><button onclick="doLogout()" style="width:auto;padding:6px 12px;background:#ff0040;color:#fff;border:none;border-radius:8px">Logout</button></div>
<div style="padding:8px;background:#000;border-bottom:2px solid #00ff88"><b style="color:#00ff88;font-size:11px">ONLINE FRIENDS - Click CALL - WILL come to called number!</b><br><small>Your ID: <span id="myIdShow" style="color:#00ff88"></span></small></div>
<div id="online"><div style="padding:20px;text-align:center;color:#aaa">Connecting...</div></div>
</div>
<div id="incoming">
<h2 style="color:#00ff88;font-size:30px">TAMY CALL!</h2>
<p id="callFrom" style="margin:15px;text-align:center;line-height:1.6"></p>
<div style="display:flex;gap:15px;margin-top:25px">
<button class="green" style="padding:18px 35px;font-size:18px" onclick="doAnswer()">Answer</button>
<button style="padding:18px 35px;background:#ff0040;color:#fff;border:none;border-radius:10px;font-weight:900;font-size:18px" onclick="doDecline()">Decline</button>
</div>
</div>
<div id="voice">
<h2 id="vStatus">CALLING...</h2>
<p id="vTimer" style="color:#00ff88;font-size:26px;margin:12px">00:00</p>
<p id="vWith" style="color:#aaa;text-align:center"></p>
<div style="display:flex;gap:12px;margin-top:25px">
<button style="padding:12px 22px;background:#1a1a2e;color:#fff;border:none;border-radius:20px;font-weight:900" onclick="doMute()">Mute</button>
<button style="padding:12px 22px;background:#ff0040;color:#fff;border:none;border-radius:20px;font-weight:900" onclick="doEnd()">End</button>
</div>
</div>
<script>
var ws=null,pcs={},localStream=null,timer=null,sec=0,incomingFrom=null,incomingName='',myId='',myName='',myNum='',isMuted=false;
function showAlert(t){var e=document.getElementById('alert');e.innerText=t;e.style.display='block';setTimeout(function(){e.style.display='none'},4000);console.log(t);}
function doNewId(){var id='tamy_'+Math.random().toString(36).substring(2,7);document.getElementById('myid').value=id;document.getElementById('msg').innerText='New ID: '+id+' - Friend MUST use DIFFERENT!';showAlert('New ID: '+id);}
function doRegister(){var name=document.getElementById('n').value.trim();var num=document.getElementById('num').value.trim();var id=document.getElementById('myid').value.trim();if(!name||!num||!id){showAlert('Fill all!');return;}myId=id;myName=name;myNum=num;localStorage.setItem('tamy_token',myId);localStorage.setItem('tamy_name',myName);localStorage.setItem('tamy_number',myNum);localStorage.setItem('tamy_verified','true');document.getElementById('loginBox').style.display='none';document.getElementById('main').style.display='flex';document.getElementById('myIdShow').innerText=myId;connectWS();}
function doLogin(){var name=document.getElementById('n').value.trim();var num=document.getElementById('num').value.trim();var id=document.getElementById('myid').value.trim();if(!name||!num||!id){showAlert('Fill all!');return;}myId=id;myName=name;myNum=num;localStorage.setItem('tamy_token',myId);localStorage.setItem('tamy_name',myName);localStorage.setItem('tamy_number',myNum);localStorage.setItem('tamy_verified','true');document.getElementById('loginBox').style.display='none';document.getElementById('main').style.display='flex';document.getElementById('myIdShow').innerText=myId;connectWS();}
function doLogout(){localStorage.clear();location.reload();}
function connectWS(){
 if(!myId)return;if(ws){try{ws.close();}catch(e){}}
 var proto=location.protocol==='https:'?'wss:':'ws:';
 var url=proto+'//'+location.host+'/ws/tamy?token='+encodeURIComponent(myId)+'&name='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNum);
 console.log('Connecting:',url);
 ws=new WebSocket(url);
 ws.onopen=function(){showAlert('Connected! ID: '+myId);console.log('WS OPEN');};
 ws.onmessage=function(ev){
  console.log('WS MSG:',ev.data);
  var d=JSON.parse(ev.data);
  if(d.type==='users'){
   var users=d.users||[];
   var otherCount=0;
   var html='';
   for(var i=0;i<users.length;i++){var u=users[i];if(u.id===myId)continue;otherCount++;html+='<div class="userRow"><div><b>'+u.name+'</b><br><span style="color:#00ff88">'+(u.number||'')+'</span><br><small style="color:#aaa">'+u.id+'</small><br><small style="color:#00ff88">Will receive call!</small></div><div><button class="green" style="padding:12px 18px;width:auto" onclick="doCall(\\''+u.id+'\\',\\''+u.name+'\\')">CALL</button></div></div>';}
   document.getElementById('count').innerText=otherCount+' Online';
   if(html===''){html='<div style="padding:20px;background:#000;border-radius:12px;border:2px dashed #00ff88;color:#aaa;font-size:12px;line-height:1.6;text-align:left"><b style="color:#00ff88">YOU ARE ALONE - THIS IS WHY 0 ONLINE!</b><br><br>Your current ID: <b style="color:#00ff88">'+myId+'</b><br><br><b style="color:#fff">TO TEST CALLS COMING TO CALLED NUMBER:</b><br>1. Press <b>Ctrl+Shift+N</b> (Incognito window)<br>2. Open same Render link<br>3. Click Create New ID - MUST BE DIFFERENT!<br>Example: Tab1: tamy_shafik123<br>Tab2: tamy_king456<br>4. Register both tabs<br>5. You will see 1 Online and CALL button<br>6. Click CALL - Other tab WILL get TAMY CALL! popup<br><br><span style="color:#ff00aa">If you use SAME ID in 2 tabs, it will still show 0 Online!</span></div>';}
   document.getElementById('online').innerHTML=html;
  }
  if(d.type==='signal'){handleSignal(d);}
 };
 ws.onerror=function(e){console.log('WS error',e);showAlert('WS error - Check Render logs');document.getElementById('online').innerHTML='<div style="padding:15px;background:#ff004020;border-radius:10px;color:#ff0040">WebSocket error - Render restarting - Wait 30 sec and refresh</div>';};
 ws.onclose=function(e){console.log('WS closed',e.code);if(myId&&e.code!==1000){setTimeout(connectWS,2000);}};
}
function doCall(targetId,targetName){
 if(!targetId){showAlert('No friend online! Open 2nd tab incognito with DIFFERENT ID!');return;}
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(s){
  localStream=s;
  document.getElementById('voice').style.display='flex';
  document.getElementById('vStatus').innerText='Calling '+targetName+'...';
  document.getElementById('vWith').innerText='To: '+targetName+' ID: '+targetId+' - Called number WILL get popup! Check other tab!';
  sec=0;document.getElementById('vTimer').innerText='00:00';if(timer)clearInterval(timer);
  timer=setInterval(function(){sec++;var m=String(Math.floor(sec/60)).padStart(2,'0');var ss=String(sec%60).padStart(2,'0');document.getElementById('vTimer').innerText=m+':'+ss;},1000);
  var payload={type:'signal',to:targetId,data:{type:'voice_call',callerName:myName,callerNumber:myNum,callerId:myId}};
  ws.send(JSON.stringify(payload));
  showAlert('Call sent to '+targetName+' - Other tab WILL ring!');
 }).catch(function(e){showAlert('Allow mic: '+e.message);});
}
function createPC(id){
 var pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'},{urls:'turn:openrelay.metered.ca:80',username:'openrelayproject',credential:'openrelayproject'},{urls:'turn:openrelay.metered.ca:443',username:'openrelayproject',credential:'openrelayproject'}]});
 pc.onicecandidate=function(e){if(e.candidate&&ws){ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate}}));}};
 pc.ontrack=function(e){var a=document.createElement('audio');a.autoplay=true;a.style.display='none';a.srcObject=e.streams[0];document.body.appendChild(a);showAlert('Connected to '+id.substring(0,6)+'!');};
 if(localStream){localStream.getTracks().forEach(function(t){pc.addTrack(t,localStream);});}
 pcs[id]=pc;return pc;
}
function handleSignal(d){
 var from=d.from;var data=d.data||{};var fromName=d.fromName||'Friend';var fromNumber=d.fromNumber||'';
 if(data.type==='voice_call'){
  incomingFrom=from;incomingName=fromName;
  document.getElementById('incoming').style.display='flex';
  document.getElementById('callFrom').innerHTML=fromName+' is calling you...<br>Number: <b style="color:#ff00aa">'+fromNumber+'</b><br>ID: '+from+'<br><br><span style="color:#00ff88;font-weight:900">Click Answer! Call coming to called number!</span>';
  showAlert('INCOMING CALL from '+fromName);
  if(navigator.vibrate){navigator.vibrate([500,200,500,200,500]);}
 }
 if(data.type==='offer'){var pc=createPC(from);pc.setRemoteDescription(new RTCSessionDescription(data)).then(function(){return pc.createAnswer();}).then(function(ans){return pc.setLocalDescription(ans);}).then(function(){ws.send(JSON.stringify({type:'signal',to:from,data:pcs[from].localDescription}));});}
 if(data.type==='answer'){var pc=pcs[from];if(pc){pc.setRemoteDescription(new RTCSessionDescription(data));}}
 if(data.candidate){var pc=pcs[from];if(pc){try{pc.addIceCandidate(new RTCIceCandidate(data.candidate));}catch(e){}}}
 if(data.type==='decline'){showAlert('Declined');doEnd();}
}
function doAnswer(){
 if(!incomingFrom){showAlert('No call');return;}
 document.getElementById('incoming').style.display='none';
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(s){
  localStream=s;
  document.getElementById('voice').style.display='flex';
  document.getElementById('vStatus').innerText='Connected to '+incomingName;
  document.getElementById('vWith').innerText='Answered! Connected!';
  sec=0;if(timer)clearInterval(timer);
  timer=setInterval(function(){sec++;var m=String(Math.floor(sec/60)).padStart(2,'0');var ss=String(sec%60).padStart(2,'0');document.getElementById('vTimer').innerText=m+':'+ss;},1000);
  var pc=createPC(incomingFrom);
  return pc.createOffer().then(function(off){return pc.setLocalDescription(off);}).then(function(){ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:pcs[incomingFrom].localDescription}));showAlert('Answered!');});
 }).catch(function(e){showAlert('Allow mic: '+e.message);});
 incomingFrom=null;
}
function doDecline(){if(incomingFrom&&ws){ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:{type:'decline'}}));}document.getElementById('incoming').style.display='none';incomingFrom=null;showAlert('Declined');}
function doEnd(){document.getElementById('voice').style.display='none';if(timer){clearInterval(timer);}sec=0;if(localStream){localStream.getTracks().forEach(function(t){t.stop();});localStream=null;}for(var k in pcs){try{pcs[k].close();}catch(e){}}pcs={};var audios=document.querySelectorAll('audio');for(var i=0;i<audios.length;i++){audios[i].remove();}}
function doMute(){if(!localStream)return;isMuted=!isMuted;localStream.getAudioTracks().forEach(function(t){t.enabled=!isMuted;});showAlert(isMuted?'Muted':'Mic On');}
var saved=localStorage.getItem('tamy_token');
if(saved){
 document.getElementById('n').value=localStorage.getItem('tamy_name')||'';
 document.getElementById('num').value=localStorage.getItem('tamy_number')||'';
 document.getElementById('myid').value=saved;
 myId=saved;myName=localStorage.getItem('tamy_name')||'';myNum=localStorage.getItem('tamy_number')||'';
 if(localStorage.getItem('tamy_verified')==='true'){document.getElementById('loginBox').style.display='none';document.getElementById('main').style.display='flex';document.getElementById('myIdShow').innerText=myId;connectWS();}
}
</script></body></html>
    """)

@app.websocket("/ws/tamy")
@app.websocket("/ws/tamy/")
async def ws_tamy(websocket: WebSocket, token: str = "", name: str = "User", number: str = ""):
    await websocket.accept()
    cid = token or f"user_{id(websocket)}"
    clients[cid] = {"ws": websocket, "name": name, "number": number}
    await broadcast()
    try:
        while True:
            raw = await websocket.receive_text()
            j = json.loads(raw)
            target = j.get("to")
            j["from"] = cid
            j["fromName"] = clients.get(cid, {}).get("name", "Friend")
            j["fromNumber"] = clients.get(cid, {}).get("number", "")
            if target and target in clients:
                try:
                    await clients[target]["ws"].send_text(json.dumps(j))
                except:
                    pass
            else:
                for oid, c in list(clients.items()):
                    if oid!= cid:
                        try:
                            await c["ws"].send_text(json.dumps(j))
                        except:
                            pass
    except WebSocketDisconnect:
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
