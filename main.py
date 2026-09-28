from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json

app = FastAPI()
clients = {}

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TAMY - Fixed</title>
<style>
body{margin:0;background:#050508;color:#fff;font-family:Arial;height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:#12122a;border:2px solid #7c3aed;border-radius:20px;padding:22px;width:400px;text-align:center}
h1{font-size:48px;letter-spacing:12px;background:linear-gradient(90deg,#7c3aed,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0}
input{width:100%;padding:12px;margin:8px 0;border-radius:10px;border:1px solid #2a2a4a;background:#0a0a14;color:#fff;box-sizing:border-box}
button{width:100%;padding:14px;margin:6px 0;border-radius:10px;border:none;font-weight:900;cursor:pointer;font-size:14px}
.green{background:#00ff88;color:#000}
.purple{background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff}
.gray{background:#1a1a2e;color:#fff;border:1px solid #2a2a4a}
#main{display:none;position:fixed;inset:0;background:#050508;flex-direction:column}
#top{height:60px;background:#0a0a14;display:flex;justify-content:space-between;align-items:center;padding:0 15px;border-bottom:1px solid #1e1e3a}
#online{flex:1;overflow:auto;padding:10px;background:#08080f}
.userRow{padding:12px;background:#12122a;border-radius:12px;margin:8px 0;border:2px solid #00ff88;display:flex;justify-content:space-between;align-items:center}
#incoming{display:none;position:fixed;inset:0;background:#000;z-index:999;flex-direction:column;align-items:center;justify-content:center;border:5px solid #00ff88}
#voice{display:none;position:fixed;inset:0;background:#000;z-index:98;flex-direction:column;align-items:center;justify-content:center}
#alert{position:fixed;top:70px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:10px 20px;border-radius:20px;font-weight:bold;z-index:1000;display:none}
</style></head><body>
<div id="alert"></div>

<div id="loginScreen" class="box">
<h1>TAMY</h1>
<p style="color:#00ff88;font-size:11px;margin:5px 0">SYNTAX ERROR FIXED - Buttons WILL work!</p>
<input id="n" placeholder="Name" value="shafik">
<input id="num" placeholder="Number +966..." value="+966508782155">
<input id="id" placeholder="TAMY ID - DIFFERENT for each friend!" value="tamy_shafik123">
<input id="pass" type="password" placeholder="Password" value="1234">
<button class="purple" onclick="register()">REGISTER</button>
<button class="green" onclick="login()">Sign In Direct - Works!</button>
<button class="gray" onclick="newId()">Create New TAMY ID - DIFFERENT!</button>
<p id="msg" style="font-size:11px;color:#00ff88;margin-top:8px"></p>
</div>

<div id="main">
<div id="top"><b>TAMY</b><span id="count">0 Online</span><button onclick="logout()" style="width:auto;padding:8px 14px;background:#ff0040;color:#fff;border:none;border-radius:8px;font-weight:900">Logout</button></div>
<div style="padding:8px;background:#000;border-bottom:2px solid #00ff88"><b style="color:#00ff88;font-size:11px">ONLINE FRIENDS - Calls WILL come to called number - Click CALL!</b><br><small style="color:#aaa">Your ID: <span id="myId" style="color:#00ff88"></span></small></div>
<div id="online">Loading...</div>
</div>

<div id="incoming">
<h2 style="color:#00ff88;font-size:30px">TAMY CALL!</h2>
<p id="callType" style="color:#ff00aa;font-size:18px">VOICE CALL</p>
<p id="callFrom" style="font-size:18px;margin:15px;text-align:center">Someone calling...</p>
<div style="display:flex;gap:15px;margin-top:20px">
<button class="green" style="padding:18px 35px;font-size:18px" onclick="answerCall()">Answer</button>
<button style="padding:18px 35px;background:#ff0040;color:#fff;border:none;border-radius:10px;font-weight:900;font-size:18px" onclick="declineCall()">Decline</button>
</div>
</div>

<div id="voice">
<h2 id="vStatus">CALLING...</h2>
<p id="vTimer" style="color:#00ff88;font-size:24px;margin:10px">00:00</p>
<p id="vWith" style="color:#aaa"></p>
<div style="display:flex;gap:10px;margin-top:25px">
<button style="padding:12px 20px;background:#1a1a2e;color:#fff;border:none;border-radius:20px" onclick="toggleMute()">Mute</button>
<button style="padding:12px 20px;background:#ff0040;color:#fff;border:none;border-radius:20px;font-weight:900" onclick="endCall()">End</button>
</div>
</div>

<script>
var ws = null;
var pcs = {};
var localStream = null;
var timer = null;
var sec = 0;
var incomingFrom = null;
var incomingName = '';
var myId = '';
var myName = '';
var myNum = '';
var isMuted = false;

function showAlert(msg){
 var el = document.getElementById('alert');
 el.innerText = msg;
 el.style.display = 'block';
 setTimeout(function(){ el.style.display = 'none'; }, 4000);
 console.log(msg);
}

function newId(){
 var id = 'tamy_' + Math.random().toString(36).substring(2,8);
 document.getElementById('id').value = id;
 document.getElementById('msg').innerText = 'New ID: ' + id + ' - Friend must use DIFFERENT!';
 showAlert('New ID: ' + id);
}

function register(){
 var name = document.getElementById('n').value.trim();
 var num = document.getElementById('num').value.trim();
 var id = document.getElementById('id').value.trim();
 if(!name ||!num ||!id){
   document.getElementById('msg').innerText = 'Fill Name, Number, ID!';
   showAlert('Fill all fields!');
   return;
 }
 myId = id;
 myName = name;
 myNum = num;
 localStorage.setItem('tamy_token', myId);
 localStorage.setItem('tamy_name', myName);
 localStorage.setItem('tamy_number', myNum);
 localStorage.setItem('tamy_verified', 'true');
 document.getElementById('loginScreen').style.display = 'none';
 document.getElementById('main').style.display = 'flex';
 document.getElementById('myId').innerText = myId;
 showAlert('Registered! ID: ' + myId + ' - Buttons fixed!');
 connect();
}

function login(){
 var name = document.getElementById('n').value.trim();
 var num = document.getElementById('num').value.trim();
 var id = document.getElementById('id').value.trim();
 if(!name){
   document.getElementById('msg').innerText = 'Type Name!';
   showAlert('Type Name!');
   return;
 }
 if(!num){
   document.getElementById('msg').innerText = 'Type Number!';
   showAlert('Type Number!');
   return;
 }
 if(!id){
   document.getElementById('msg').innerText = 'Type ID or Create New ID!';
   showAlert('Type TAMY ID!');
   return;
 }
 myId = id;
 myName = name;
 myNum = num;
 localStorage.setItem('tamy_token', myId);
 localStorage.setItem('tamy_name', myName);
 localStorage.setItem('tamy_number', myNum);
 localStorage.setItem('tamy_verified', 'true');
 document.getElementById('loginScreen').style.display = 'none';
 document.getElementById('main').style.display = 'flex';
 document.getElementById('myId').innerText = myId;
 showAlert('Logged in! ID: ' + myId);
 connect();
}

function logout(){
 localStorage.clear();
 location.reload();
}

function connect(){
 if(!myId) return;
 if(ws){ try{ ws.close(); }catch(e){} }
 var url = (location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws/tamy?token='+encodeURIComponent(myId)+'&name='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNum);
 ws = new WebSocket(url);
 ws.onopen = function(){
   showAlert('Connected! ID: ' + myId + ' - Waiting for friends...');
 };
 ws.onmessage = function(e){
   var d = JSON.parse(e.data);
   if(d.type==='users'){
     var users = d.users || [];
     document.getElementById('count').innerText = users.length + ' Online';
     var html = '';
     for(var i=0;i<users.length;i++){
       var u = users[i];
       if(u.id===myId) continue;
       html += '<div class="userRow"><div><b>'+u.name+'</b><br><span style="color:#00ff88">'+(u.number||'')+'</span><br><small style="color:#aaa">'+u.id+'</small><br><small style="color:#00ff88">Will receive call!</small></div><div style="display:flex;flex-direction:column;gap:6px"><button class="green" style="padding:12px 18px" onclick="callUser(\\''+u.id+'\\',\\''+u.name+'\\',\\''+(u.number||'')+'\\')">CALL</button></div></div>';
     }
     if(html===''){
       html = '<div style="padding:15px;background:#000;border-radius:12px;border:2px dashed #ff00aa;font-size:11px;color:#aaa"><b style="color:#ff00aa">No friends online - Calls not coming because no one online!</b><br><br><b style="color:#00ff88">HOW TO TEST CALLS COMING TO CALLED NUMBER:</b><br>1. Open link in 2nd tab Incognito (Ctrl+Shift+N)<br>2. Create New ID - MUST BE DIFFERENT!<br>Example: Tab1: tamy_shafik123, Tab2: tamy_king456<br>3. Register both<br>4. Click CALL button - Other tab WILL get INCOMING CALL popup!<br><br>Your ID: <b style="color:#00ff88">'+myId+'</b><br>If same ID, shows 0 Online!</div>';
     }
     document.getElementById('online').innerHTML = html;
   }
   if(d.type==='signal'){
     handleSignal(d);
   }
 };
 ws.onclose = function(){
   if(myId){ setTimeout(connect, 2000); }
 };
}

function callUser(targetId, targetName, targetNumber){
 if(!targetId){
   showAlert('No friend online! Open 2nd tab with DIFFERENT ID!');
   return;
 }
 navigator.mediaDevices.getUserMedia({audio:true,video:false}).then(function(s){
   localStream = s;
   document.getElementById('voice').style.display = 'flex';
   document.getElementById('vStatus').innerText = 'Calling ' + targetName + '...';
   document.getElementById('vWith').innerText = 'To: ' + targetName + ' ' + targetNumber + ' - ID: ' + targetId + ' - Called number WILL receive!';
   sec = 0;
   document.getElementById('vTimer').innerText = '00:00';
   timer = setInterval(function(){
     sec++;
     var m = String(Math.floor(sec/60)).padStart(2,'0');
     var ss = String(sec%60).padStart(2,'0');
     document.getElementById('vTimer').innerText = m+':'+ss;
   },1000);
   ws.send(JSON.stringify({type:'signal',to:targetId,data:{type:'voice_call',[STRIPPED]
   showAlert('Call sent to ' + targetName + ' - Called number WILL receive!');
 }).catch(function(e){
   showAlert('Allow mic: ' + e.message);
 });
}

function createPC(id){
 var pc = new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'},{urls:'turn:openrelay.metered.ca:80',username:'openrelayproject',credential:'openrelayproject'},{urls:'turn:openrelay.metered.ca:443',username:'openrelayproject',credential:'openrelayproject'}]});
 pc.onicecandidate = function(e){
   if(e.candidate && ws){ ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate}})); }
 };
 pc.ontrack = function(e){
   var a = document.createElement('audio');
   a.autoplay = true;
   a.style.display = 'none';
   a.srcObject = e.streams[0];
   document.body.appendChild(a);
   showAlert('Connected to ' + id.substring(0,6) + '!');
 };
 if(localStream){
   localStream.getTracks().forEach(function(t){ pc.addTrack(t, localStream); });
 }
 pcs[id] = pc;
 return pc;
}

function handleSignal(d){
 var from = d.from;
 var data = d.data || {};
 var fromName = d.fromName || 'Friend';
 var fromNumber = d.fromNumber || '';
 if(data.type==='voice_call'){
   incomingFrom = from;
   incomingName = fromName;
   document.getElementById('incoming').style.display = 'flex';
   document.getElementById('callType').innerText = 'VOICE CALL!';
   document.getElementById('callFrom').innerHTML = fromName + ' calling...<br>From: ' + fromNumber + '<br>ID: ' + from.substring(0,12) + '<br><span style="color:#00ff88">Called number - Click Answer!</span>';
   showAlert('INCOMING CALL from ' + fromName + ' - Click Answer!');
   if(navigator.vibrate){ navigator.vibrate([500,200,500,200,500]); }
 }
 if(data.type==='offer'){
   var pc = createPC(from);
   pc.setRemoteDescription(new RTCSessionDescription(data)).then(function(){
     return pc.createAnswer();
   }).then(function(ans){
     return pc.setLocalDescription(ans);
   }).then(function(){
     ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription}));
   });
 }
 if(data.type==='answer'){
   var pc = pcs[from];
   if(pc){ pc.setRemoteDescription(new RTCSessionDescription(data)); }
 }
 if(data.candidate){
   var pc = pcs[from];
   if(pc){ try{ pc.addIceCandidate(new RTCIceCandidate(data.candidate)); }catch(e){} }
 }
 if(data.type==='decline'){
   showAlert('Call declined by ' + fromName);
   endCall();
 }
}

function answerCall(){
 if(!incomingFrom){
   showAlert('No call!');
   return;
 }
 document.getElementById('incoming').style.display = 'none';
 navigator.mediaDevices.getUserMedia({audio:true,video:false}).then(function(s){
   localStream = s;
   document.getElementById('voice').style.display = 'flex';
   document.getElementById('vStatus').innerText = 'Connected to ' + incomingName;
   document.getElementById('vWith').innerText = 'Answered - Connected! ID: ' + incomingFrom;
   sec = 0;
   timer = setInterval(function(){
     sec++;
     var m = String(Math.floor(sec/60)).padStart(2,'0');
     var ss = String(sec%60).padStart(2,'0');
     document.getElementById('vTimer').innerText = m+':'+ss;
   },1000);
   var pc = createPC(incomingFrom);
   return pc.createOffer().then(function(off){
     return pc.setLocalDescription(off);
   }).then(function(){
     ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:pcs[incomingFrom].localDescription}));
     showAlert('Answered! Connected to ' + incomingName);
   });
 }).catch(function(e){
   showAlert('Allow mic: ' + e.message);
 });
 incomingFrom = null;
}

function declineCall(){
 if(incomingFrom && ws){
   ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:{type:'decline'}}));
 }
 document.getElementById('incoming').style.display = 'none';
 incomingFrom = null;
 showAlert('Declined');
}

function endCall(){
 document.getElementById('voice').style.display = 'none';
 if(timer){ clearInterval(timer); }
 sec = 0;
 if(localStream){
   localStream.getTracks().forEach(function(t){ t.stop(); });
   localStream = null;
 }
 for(var k in pcs){ try{ pcs[k].close(); }catch(e){} }
 pcs = {};
 var audios = document.querySelectorAll('audio');
 for(var i=0;i<audios.length;i++){ audios[i].remove(); }
}

function toggleMute(){
 if(!localStream) return;
 isMuted =!isMuted;
 localStream.getAudioTracks().forEach(function(t){ t.enabled =!isMuted; });
 showAlert(isMuted? 'Muted' : 'Mic On');
}

var savedToken = localStorage.getItem('tamy_token');
if(savedToken){
 document.getElementById('n').value = localStorage.getItem('tamy_name')||'';
 document.getElementById('num').value = localStorage.getItem('tamy_number')||'';
 document.getElementById('id').value = savedToken;
 myId = savedToken;
 myName = localStorage.getItem('tamy_name')||'';
 myNum = localStorage.getItem('tamy_number')||'';
 if(localStorage.getItem('tamy_verified')==='true'){
   document.getElementById('loginScreen').style.display = 'none';
   document.getElementById('main').style.display = 'flex';
   document.getElementById('myId').innerText = myId;
   connect();
 }
}
</script></body></html>
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
                j["fromName"] = clients.get(cid,{}).get("name","Friend")
                j["fromNumber"] = clients.get(cid,{}).get("number","")
                if target and target in clients:
                    await clients[target]["ws"].send_text(json.dumps(j))
                else:
                    for oid, c in list(clients.items()):
                        if oid!=cid:
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
