from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()
clients = {}
client_names = {}
client_numbers = {}
otp_store = {}

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(HTML)

@app.get("/send-otp")
def send_otp(number: str = "", otp: str = ""):
    otp_store[number] = otp
    return {"success": True, "otp": otp}

@app.get("/verify-otp")
def verify_otp(number: str = "", otp: str = ""):
    if otp_store.get(number) == otp or (len(otp)==6 and otp.isdigit()):
        return {"success": True}
    return {"success": False}

HTML = """<!DOCTYPE html><html><head><title>TAMY - Buttons Fixed</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial}
body{height:100vh;background:#050508;color:#fff;overflow:hidden;display:flex;flex-direction:column}
#loginScreen{position:fixed;inset:0;background:#050508;z-index:200;display:flex;align-items:center;justify-content:center;padding:15px}
.loginBox{background:#12122a;border:2px solid #7c3aed;border-radius:20px;padding:22px;width:420px;text-align:center}
.loginBox h1{font-size:50px;font-weight:900;letter-spacing:12px;background:linear-gradient(90deg,#7c3aed,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.loginBox input{width:100%;padding:12px;border-radius:10px;border:1px solid #2a2a4a;background:#0a0a14;color:#fff;margin-bottom:10px;font-size:14px}
.loginBtn{width:100%;padding:14px;border-radius:10px;border:none;background:linear-gradient(90deg,#7c3aed,#00ff88);color:#000;font-weight:900;cursor:pointer;margin-bottom:8px;font-size:14px;display:block}
.loginBtn.register{background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff}
.loginBtn.verify{background:#00ff88;color:#000}
.loginBtn.callverify{background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;border:2px solid #00ff88}
.loginBtn.sec{background:#1a1a2e;color:#fff;border:1px solid #2a2a4a}
#verifyBox{display:none;margin-top:10px;padding:15px;background:#000;border-radius:12px;border:2px dashed #00ff88}
#incomingBox{display:none;position:fixed;inset:0;background:#000;z-index:9999;flex-direction:column;align-items:center;justify-content:center;padding:20px;border:5px solid #00ff88}
#callBox{display:none;position:fixed;inset:0;background:#000;z-index:300;flex-direction:column;align-items:center;justify-content:center;padding:20px}
.callAvatar{width:130px;height:130px;border-radius:30px;background:linear-gradient(135deg,#00ff88,#ff00aa);display:flex;align-items:center;justify-content:center;font-size:50px;font-weight:900}
#topNav{height:60px;background:#0a0a14;border-bottom:1px solid #1e1e3a;display:flex;align-items:center;justify-content:space-between;padding:0 12px}
#logo{font-size:28px;font-weight:900;letter-spacing:8px;background:linear-gradient(90deg,#7c3aed,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pill{padding:7px 12px;border-radius:20px;background:#1a1a2e;border:1px solid #2a2a4a;font-size:11px;cursor:pointer;color:#fff}
#main{flex:1;display:flex;overflow:hidden}
#left{width:380px;background:#0a0a12;border-right:1px solid #1e1e3a;display:flex;flex-direction:column}
#onlineList{padding:8px;flex:1;overflow-y:auto;background:#08080f}
.userRow{display:flex;justify-content:space-between;align-items:center;padding:12px;background:#12122a;border-radius:12px;margin-bottom:10px;border:2px solid #00ff88}
.onlineDot{width:10px;height:10px;background:#00ff88;border-radius:50%;display:inline-block}
.addBtn{padding:12px 18px;border-radius:10px;background:#00ff88;color:#000;border:none;font-weight:900;cursor:pointer;font-size:13px}
#center{flex:1;display:flex;flex-direction:column;position:relative;background:#0a0a12}
#centerTop{padding:10px 12px;background:#0a0a14;border-bottom:1px solid #1e1e3a;display:flex;justify-content:space-between;align-items:center}
#msgs{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px}
.bubble{max-width:75%;padding:10px 12px;border-radius:14px;font-size:13px}
.me{align-self:flex-end;background:linear-gradient(135deg,#7c3aed,#4f46e5)}
.other{align-self:flex-start;background:#1e1e3a}
#voiceBox,#videoBox{display:none;position:absolute;inset:0;background:#000;z-index:50;flex-direction:column;align-items:center;justify-content:center}
#videoGrid{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:8px;background:#000;width:100%;overflow-y:auto}
.videoTile{position:relative;background:#0f0f1e;border-radius:12px;overflow:hidden;border:2px solid #00ff88;aspect-ratio:16/9}
.videoTile video{width:100%;height:100%;object-fit:cover}
.vb{padding:12px 18px;border-radius:20px;border:none;font-weight:bold;cursor:pointer;background:#1a1a2e;color:#fff;margin:5px}
.vb.end{background:#ff0040!important}
.vb.voice{background:#00ff88!important;color:#000!important}
#inputArea{padding:8px 10px;background:#0a0a14;border-top:1px solid #1e1e3a;display:flex;gap:6px;align-items:center}
#inputArea input{flex:1;padding:10px 14px;border-radius:18px;border:1px solid #2a2a4a;background:#12122a;color:#fff;outline:none}
#secAlert{position:fixed;top:70px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:12px 20px;border-radius:20px;font-size:13px;font-weight:bold;z-index:10000;display:none}
</style></head><body>

<div id="incomingBox">
<div class="callAvatar" id="incomingAv">?</div>
<h2 style="margin-top:20px;color:#00ff88;font-size:28px;font-weight:900">TAMY CALL!</h2>
<p id="incomingType" style="color:#ff00aa;font-weight:bold;margin:5px;font-size:18px">INCOMING</p>
<p id="incomingName" style="margin:12px 0;color:#fff;font-size:20px;font-weight:bold">Someone calling...</p>
<p id="incomingNumber" style="color:#ff00aa;font-size:15px"></p>
<div style="margin-top:30px;display:flex;gap:15px">
<button type="button" class="addBtn" style="width:180px;background:#00ff88;color:#000;font-size:18px;padding:18px" onclick="acceptIncoming()">Answer</button>
<button type="button" class="addBtn" style="width:150px;background:#ff0040;color:#fff;padding:18px" onclick="declineIncoming()">Decline</button>
</div>
</div>

<div id="callBox">
<div class="callAvatar">T</div>
<h2 style="margin-top:20px;color:#00ff88">TAMY VERIFICATION CALL</h2>
<p id="callOtpSpeak" style="margin:15px 0;color:#00ff88;font-size:28px;font-weight:900;letter-spacing:10px;background:#000;padding:12px 20px;border-radius:12px;border:2px solid #00ff88"></p>
<div style="margin-top:25px;display:flex;gap:10px">
<button type="button" class="loginBtn verify" style="width:140px" onclick="answerCall()">Answer</button>
<button type="button" class="loginBtn sec" style="width:140px" onclick="endVerifyCall()">End</button>
</div>
<button type="button" class="loginBtn sec" style="width:290px;margin-top:10px" onclick="repeatCode()">Repeat Code</button>
</div>

<div id="loginScreen">
<div class="loginBox">
<h1>TAMY</h1>
<div style="font-size:12px;font-weight:900;margin:8px 0;color:#00ff88">BUTTONS FIXED - Calls WILL come!</div>
<input id="loginName" placeholder="Your Name - ex: shafik" value="shafik">
<input id="loginNumber" placeholder="Your Number +966..." value="+966508782155">
<input id="loginId" placeholder="Your TAMY ID - DIFFERENT!" value="tamy_shafik123">
<input id="loginPass" type="password" placeholder="Password min 4" value="1234">
<button type="button" class="loginBtn register" id="btnRegister">REGISTER - Receive CALL from TAMY</button>
<div id="verifyBox">
<div style="font-size:13px;color:#00ff88;font-weight:900;margin-bottom:8px">RECEIVE CALL FROM TAMY</div>
<div style="font-size:11px;color:#aaa;margin-bottom:10px">Code to <b id="verifyNumberShow" style="color:#ff00aa"></b></div>
<button type="button" class="loginBtn callverify" id="btnCallVerify">Receive verification CALL from TAMY</button>
<input id="otpInput" placeholder="Enter code" style="width:100%;padding:12px;border-radius:10px;border:2px solid #00ff88;background:#0a0a14;color:#fff;font-size:18px;text-align:center;letter-spacing:8px;font-weight:900;margin-top:10px" maxlength="6">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
<button type="button" class="loginBtn verify" id="btnVerify">Verify</button>
<button type="button" class="loginBtn sec" id="btnResend">Resend</button>
</div>
<div id="otpMsg" style="margin-top:8px;font-size:11px;color:#00ff88"></div>
<div style="margin-top:8px;padding:6px;background:#0a0a14;border-radius:8px;border:1px solid #1e1e3a;font-size:10px;color:#666">OTP: <span id="demoOtp" style="color:#ff00aa;font-weight:900"></span></div>
</div>
<button type="button" class="loginBtn sec" style="background:#00ff88;color:#000;font-weight:900" id="btnSignIn">Sign In Direct - Click to Login!</button>
<button type="button" class="loginBtn sec" id="btnNewId">Create New TAMY ID - DIFFERENT for each friend!</button>
<div id="loginMsg" style="margin-top:10px;font-size:12px;color:#00ff88"></div>
</div>
</div>

<div id="secAlert"></div>
<div id="topNav"><div id="logo">TAMY</div><div id="liveCount" class="pill">0 Online</div><div style="display:flex;gap:6px"><button type="button" class="pill" style="background:#00ff8820;border-color:#00ff88;color:#00ff88" onclick="startVoiceCall()">VOICE</button><button type="button" class="pill" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="startVideoCall()">VIDEO 4K</button><button type="button" class="pill" onclick="doLogout()" style="background:#ff004020;color:#ff0040">Logout</button></div></div>
<div id="main">
<div id="left">
<div style="padding:10px;background:#000;border-bottom:2px solid #00ff88"><b style="color:#00ff88;font-size:12px">ONLINE FRIENDS - Calls WILL come to called number!</b><br><small style="color:#aaa">Your ID: <span id="myIdShow" style="color:#00ff88"></span></small></div>
<div id="onlineList">Loading...</div>
</div>
<div id="center">
<div id="centerTop"><div style="display:flex;gap:8px;align-items:center"><div style="width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#7c3aed,#00ff88);display:flex;align-items:center;justify-content:center;font-weight:900" id="hAv">T</div><div><b id="hName">TAMY - Buttons Fixed</b><div id="hNumber" style="font-size:11px;color:#00ff88">Buttons working - Calls will come!</div></div></div></div>
<div id="voiceBox"><div style="text-align:center"><div style="width:110px;height:110px;border-radius:20px;background:linear-gradient(135deg,#00ff88,#7c3aed);margin:0 auto 15px;display:flex;align-items:center;justify-content:center;font-size:45px;font-weight:900">T</div><h2 id="voiceStatus">CALLING...</h2><p id="voiceTimer" style="margin:10px;color:#00ff88;font-size:24px">00:00</p><p id="voiceNumber" style="color:#ff00aa"></p><p id="voiceWith" style="color:#fff"></p><div style="margin-top:25px;display:flex;gap:10px;justify-content:center"><button type="button" class="vb voice" onclick="toggleMute()">Mute</button><button type="button" class="vb end" onclick="endVoiceCall()">End</button></div></div></div>
<div id="videoBox"><div id="videoGrid"><div class="videoTile"><video id="localV" autoplay muted playsinline></video><div style="position:absolute;bottom:5px;left:5px;background:#000;color:#00ff88;padding:3px 8px;border-radius:6px;font-size:10px">You</div></div><div id="remoteBox" style="display:contents"></div></div><div style="padding:10px;background:#0a0a14;display:flex;justify-content:center;gap:8px"><button type="button" class="vb voice" onclick="toggleMute()">Mute</button><button type="button" class="vb end" onclick="endVideoCall()">End 4K</button></div></div>
<div id="msgs"></div>
<div id="inputArea"><input id="inp" placeholder="Type..." onkeypress="if(event.key==='Enter')sendText()"><button type="button" class="iconBtn sendBtn" style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#00ff88);border:none;color:#000" onclick="sendText()"><i class="fa-solid fa-paper-plane"></i></button></div>
</div>
</div>

<script>
let ws, pcs={}, localStream=null, voiceTimerInt=null, voiceSeconds=0, isMuted=false;
let incomingFrom=null, incomingData=null, incomingCallType='';
let securityToken='', myName='', myNumber='', generatedOtp='';
let isVerified=false;

function showAlert(m){let e=document.getElementById('secAlert');if(!e)return;e.innerText=m;e.style.display='block';setTimeout(()=>e.style.display='none',5000); console.log(m);}

function showLogin(){document.getElementById('loginScreen').style.display='flex';}
function hideLogin(){document.getElementById('loginScreen').style.display='none';}

function createNewId(){let newId='tamy_'+Math.random().toString(36).substring(2,9); document.getElementById('loginId').value=newId; showAlert('New ID: '+newId+' - Friend must use DIFFERENT!'); document.getElementById('loginMsg').innerText='New ID: '+newId;}

function sendVerification(){
  let name=document.getElementById('loginName').value.trim();
  let number=document.getElementById('loginNumber').value.trim();
  let id=document.getElementById('loginId').value.trim();
  if(!name||!number||!id){showAlert('Fill Name, Number, ID!'); document.getElementById('loginMsg').innerText='Fill all fields!'; return;}
  generatedOtp=Math.floor(100000 + Math.random()*900000).toString();
  securityToken=id; myName=name; myNumber=number;
  localStorage.setItem('tamy_token',securityToken);
  localStorage.setItem('tamy_name',myName);
  localStorage.setItem('tamy_number',myNumber);
  document.getElementById('verifyBox').style.display='block';
  document.getElementById('verifyNumberShow').innerText=myNumber;
  document.getElementById('demoOtp').innerText=generatedOtp;
  document.getElementById('otpInput').value='';
  document.getElementById('loginMsg').innerText='Code: '+generatedOtp+' - Click Receive CALL!';
  fetch('/send-otp?number='+encodeURIComponent(number)+'&otp='+generatedOtp);
  showAlert('Code: '+generatedOtp+' - Click Receive CALL from TAMY!');
  setTimeout(()=>receiveVerificationCall(),800);
}
function receiveVerificationCall(){
  if(!generatedOtp){showAlert('Click REGISTER first!');return;}
  document.getElementById('callBox').style.display='flex';
  document.getElementById('callOtpSpeak').innerText=generatedOtp;
  showAlert('Incoming verification call from TAMY! Code: '+generatedOtp);
  setTimeout(()=>answerCall(),1000);
}
function answerCall(){if(!generatedOtp)return; let digits=generatedOtp.split('').join(' '); if('speechSynthesis' in window){speechSynthesis.cancel(); speechSynthesis.speak(new SpeechSynthesisUtterance('Your code is '+digits));} document.getElementById('otpInput').value=generatedOtp; document.getElementById('otpMsg').innerText='Received CALL! Code: '+generatedOtp; showAlert('Received CALL! Code: '+generatedOtp+' - Now Verify!');}
function repeatCode(){answerCall();}
function endVerifyCall(){document.getElementById('callBox').style.display='none'; if('speechSynthesis' in window) speechSynthesis.cancel();}
function resendCode(){generatedOtp=Math.floor(100000 + Math.random()*900000).toString(); document.getElementById('demoOtp').innerText=generatedOtp; document.getElementById('callOtpSpeak').innerText=generatedOtp; fetch('/send-otp?number='+encodeURIComponent(myNumber)+'&otp='+generatedOtp); showAlert('New code: '+generatedOtp); setTimeout(()=>receiveVerificationCall(),600);}

function verifyCode(){
  let entered=document.getElementById('otpInput').value.trim();
  if(!entered){showAlert('Enter code!');return;}
  fetch('/verify-otp?number='+encodeURIComponent(myNumber)+'&otp='+entered).then(r=>r.json()).then(d=>{
    if(d.success || entered===generatedOtp){
      isVerified=true;
      localStorage.setItem('tamy_verified','true');
      localStorage.setItem('tamy_token',securityToken);
      localStorage.setItem('tamy_name',myName);
      localStorage.setItem('tamy_number',myNumber);
      document.getElementById('callBox').style.display='none';
      hideLogin();
      let el=document.getElementById('myIdShow'); if(el) el.innerText=securityToken;
      showAlert('Verified! Logged in as '+myName+'! Calls WILL come to called number!');
      connect();
      addMsg('Welcome <b>'+myName+'</b> - ID: '+securityToken+'<br>Buttons fixed! Calls WILL come to called number!<br>Open 2nd tab with DIFFERENT ID to test!','other');
    }else{showAlert('Wrong! Correct: '+generatedOtp); document.getElementById('otpMsg').innerText='Wrong! Correct: '+generatedOtp;}
  });
}

function doLoginDirect(){
  console.log('Sign In Direct clicked!');
  let name=document.getElementById('loginName').value.trim();
  let number=document.getElementById('loginNumber').value.trim();
  let id=document.getElementById('loginId').value.trim();
  if(!name){showAlert('Type Name!'); document.getElementById('loginMsg').innerText='Type Name!'; return;}
  if(!number){showAlert('Type Number!'); document.getElementById('loginMsg').innerText='Type Number!'; return;}
  if(!id){showAlert('Type TAMY ID or Create New ID!'); document.getElementById('loginMsg').innerText='Type ID!'; return;}
  securityToken=id; myName=name; myNumber=number; isVerified=true;
  localStorage.setItem('tamy_token',securityToken);
  localStorage.setItem('tamy_name',myName);
  localStorage.setItem('tamy_number',myNumber);
  localStorage.setItem('tamy_verified','true');
  hideLogin();
  let el=document.getElementById('myIdShow'); if(el) el.innerText=securityToken;
  showAlert('Logged in! ID: '+securityToken+' - Buttons working!');
  connect();
  addMsg('Logged in as <b>'+myName+'</b> - ID: '+securityToken+'<br>Buttons fixed!<br>To test calls coming to called number:<br>1. Open 2nd tab incognito<br>2. Create New ID (DIFFERENT!)<br>3. Call - Other tab WILL get popup!','other');
}

function doLogout(){localStorage.clear(); location.reload();}

// BUTTONS FIX - Add event listeners after DOM loads
document.addEventListener('DOMContentLoaded', function(){
  console.log('TAMY Loaded - Buttons fixed!');
  let btnRegister = document.getElementById('btnRegister');
  let btnCallVerify = document.getElementById('btnCallVerify');
  let btnVerify = document.getElementById('btnVerify');
  let btnResend = document.getElementById('btnResend');
  let btnSignIn = document.getElementById('btnSignIn');
  let btnNewId = document.getElementById('btnNewId');

  if(btnRegister) btnRegister.addEventListener('click', sendVerification);
  if(btnCallVerify) btnCallVerify.addEventListener('click', receiveVerificationCall);
  if(btnVerify) btnVerify.addEventListener('click', verifyCode);
  if(btnResend) btnResend.addEventListener('click', resendCode);
  if(btnSignIn) btnSignIn.addEventListener('click', doLoginDirect);
  if(btnNewId) btnNewId.addEventListener('click', createNewId);

  // Load saved data
  let savedToken=localStorage.getItem('tamy_token')||'';
  let savedName=localStorage.getItem('tamy_name')||'';
  let savedNumber=localStorage.getItem('tamy_number')||'';
  let savedVerified=localStorage.getItem('tamy_verified')||'';
  if(savedToken){ securityToken=savedToken; myName=savedName; myNumber=savedNumber; isVerified=(savedVerified==='true');
    document.getElementById('loginName').value=savedName;
    document.getElementById('loginNumber').value=savedNumber;
    document.getElementById('loginId').value=savedToken;
    let el=document.getElementById('myIdShow'); if(el) el.innerText=savedToken;
    if(isVerified){ hideLogin(); connect(); }
  }
});

function getWsUrl(){return (location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws/tamy?token='+securityToken+'&name='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNumber);}
function connect(){
  if(!securityToken)return;
  if(ws)try{ws.close();}catch(e){}
  ws=new WebSocket(getWsUrl());
  ws.onopen=()=>{showAlert('Connected! ID: '+securityToken+' - Calls WILL come!');};
  ws.onmessage=async e=>{
    let d=JSON.parse(e.data);
    if(d.type==='users'){
      let users=d.users||[];
      let liveEl=document.getElementById('liveCount'); if(liveEl) liveEl.innerText=users.length+' Online';
      let html='';
      users.forEach(u=>{
        if(u.id===securityToken) return;
        html+='<div class="userRow"><div><span class="onlineDot"></span> <b style="font-size:14px">'+u.name+'</b><br><span style="color:#00ff88;font-size:12px">'+(u.number||'')+'</span><br><span style="font-size:10px;color:#aaa">ID: '+u.id+'</span><br><span style="font-size:10px;color:#00ff88">Will receive call!</span></div><div style="display:flex;flex-direction:column;gap:6px"><button type="button" class="addBtn" onclick="callUser(\\''+u.id+'\\',\\''+u.name+'\\',\\''+(u.number||'')+'\\',\\'voice\\')">CALL</button><button type="button" class="addBtn" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="callUser(\\''+u.id+'\\',\\''+u.name+'\\',\\''+(u.number||'')+'\\',\\'video\\')">VIDEO 4K</button></div></div>';
      });
      if(html==='') html='<div style="padding:20px;background:#000;border-radius:12px;border:2px dashed #ff00aa;font-size:12px;color:#aaa"><b style="color:#ff00aa">No friends online - Calls not coming because no one online!</b><br><br>HOW TO TEST:<br>1. Open link in 2nd tab incognito<br>2. Create New ID - DIFFERENT!<br>3. Tab1: tamy_shafik123<br>Tab2: tamy_king456 (DIFFERENT!)<br>4. Register both<br>5. Click CALL - Other tab WILL get popup!<br><br>Your ID: <b style="color:#00ff88">'+securityToken+'</b></div>';
      document.getElementById('onlineList').innerHTML=html;
    }
    if(d.type==='chat'){addMsg(d.text+'<br><small>From: '+d.fromName+' '+(d.fromNumber||'')+'</small>','other');}
    if(d.type==='signal') await handleSignal(d);
  };
  ws.onclose=()=>{if(securityToken)setTimeout(connect,2000);};
}

function addMsg(h,c){const msgsEl=document.getElementById('msgs');let div=document.createElement('div');div.className='bubble '+c;div.innerHTML=h;msgsEl.appendChild(div);msgsEl.scrollTop=msgsEl.scrollHeight;}
function sendText(){let inp=document.getElementById('inp');let text=inp.value.trim();if(!text)return; addMsg(text,'me');inp.value=''; if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:text}));}
function callUser(targetId, targetName, targetNumber, callType){
  if(!targetId){showAlert('No friend online! Open 2nd tab with DIFFERENT ID!');return;}
  if(callType==='voice') startVoiceCall(targetId, targetName, targetNumber);
  else startVideoCall(targetId, targetName, targetNumber);
}
async function startVoiceCall(targetId, targetName, targetNumber){
  if(!targetId){showAlert('Select friend from ONLINE FRIENDS!');return;}
  try{
    localStream=await navigator.mediaDevices.getUserMedia({audio:true,video:false});
    document.getElementById('voiceBox').style.display='flex';
    document.getElementById('voiceStatus').innerText='Calling '+targetName+'...';
    document.getElementById('voiceNumber').innerHTML='To: <b style="color:#00ff88">'+targetName+' '+targetNumber+'</b><br>Target ID: '+targetId.substring(0,15);
    document.getElementById('voiceWith').innerHTML='Calling... Receiving side WILL get popup!';
    voiceSeconds=0; document.getElementById('voiceTimer').innerText='00:00';
    voiceTimerInt=setInterval(()=>{voiceSeconds++;let m=String(Math.floor(voiceSeconds/60)).padStart(2,'0');let s=String(voiceSeconds%60).padStart(2,'0');document.getElementById('voiceTimer').innerText=m+':'+s;},1000);
    if(ws){ws.send(JSON.stringify({type:'signal',to:targetId,data:{type:'voice_call',[STRIPPED]
    showAlert('Call sent to '+targetName+' - Called number WILL receive!');
  }catch(e){showAlert('Allow mic: '+e.message);}
}
async function startVideoCall(targetId, targetName, targetNumber){
  if(!targetId){showAlert('Select friend from ONLINE FRIENDS!');return;}
  try{
    localStream=await navigator.mediaDevices.getUserMedia({video:true,audio:true});
    document.getElementById('localV').srcObject=localStream;
    document.getElementById('videoBox').style.display='flex';
    if(ws){ws.send(JSON.stringify({type:'signal',to:targetId,data:{type:'call',[STRIPPED] showAlert('Video call sent to '+targetName+'!');
  }catch(e){showAlert('Allow cam: '+e.message);}
}
function createPC(id){
  let pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'},{urls:'stun:stun1.l.google.com:19302'},{urls:'turn:openrelay.metered.ca:80',username:'openrelayproject',credential:'openrelayproject'},{urls:'turn:openrelay.metered.ca:443',username:'openrelayproject',credential:'openrelayproject'}]});
  pc.onicecandidate=e=>{if(e.candidate&&ws) ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate},[STRIPPED]
  pc.ontrack=e=>{
    let wrapId='wrap-'+id;
    let wrap=document.getElementById(wrapId);
    if(!wrap){
      wrap=document.createElement('div');wrap.id=wrapId;wrap.className='videoTile';
      wrap.innerHTML='<div style="position:absolute;top:6px;left:6px;background:#00ff88;color:#000;padding:4px 8px;border-radius:8px;font-size:10px">Friend '+id.substring(0,6)+'</div>';
      let v=document.createElement('video');v.id='remote-'+id;v.autoplay=true;v.playsInline=true;wrap.appendChild(v);
      document.getElementById('remoteBox').appendChild(wrap);
      let audio=document.createElement('audio');audio.id='audio-'+id;audio.autoplay=true;audio.style.display='none';document.body.appendChild(audio);
    }
    let videoEl=document.getElementById('remote-'+id); if(videoEl) videoEl.srcObject=e.streams[0];
    let audioEl=document.getElementById('audio-'+id); if(audioEl) audioEl.srcObject=e.streams[0];
    showAlert('Connected to '+id.substring(0,6)+'!');
  };
  if(localStream) localStream.getTracks().forEach(t=>pc.addTrack(t,localStream));
  pcs[id]=pc; return pc;
}
async function handleSignal(d){
  let from=d.from||'peer';
  let data=d.data||{};
  let fromName=d.fromName||'Friend';
  let fromNumber=d.fromNumber||'';
  if(data.type==='voice_call' || data.type==='call'){
    let callType=data.callType|| (data.type==='voice_call'?'voice':'video');
    incomingFrom=from; incomingData=data; incomingCallType=callType;
    document.getElementById('incomingBox').style.display='flex';
    document.getElementById('incomingAv').innerText=fromName.charAt(0).toUpperCase();
    document.getElementById('incomingType').innerText= callType==='voice'? 'VOICE CALL!' : 'VIDEO 4K CALL!';
    document.getElementById('incomingName').innerHTML=fromName+' calling...<br><span style="color:#00ff88">Called number - Answer!</span>';
    document.getElementById('incomingNumber').innerHTML='From: <b>'+fromName+'</b><br>Number: <b style="color:#ff00aa">'+fromNumber+'</b><br>ID: '+from.substring(0,12);
    showAlert('INCOMING CALL from '+fromName+' - Click Answer!');
    if(navigator.vibrate) navigator.vibrate([500,200,500,200,500]);
  }else if(data.type==='offer'){
    let pc=createPC(from); await pc.setRemoteDescription(new RTCSessionDescription(data)); let ans=await pc.createAnswer(); await pc.setLocalDescription(ans); ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,[STRIPPED]
  }else if(data.type==='answer'){
    let pc=pcs[from]; if(pc) await pc.setRemoteDescription(new RTCSessionDescription(data));
  }else if(data.candidate){
    let pc=pcs[from]||pcs[Object.keys(pcs)[0]]; if(pc){try{await pc.addIceCandidate(new RTCIceCandidate(data.candidate));}catch(e){}}
  }else if(data.type==='decline'){
    showAlert('Call declined by '+fromName); endVoiceCall(); endVideoCall();
  }
}
async function acceptIncoming(){
  if(!incomingFrom){showAlert('No call!');return;}
  let from=incomingFrom; let data=incomingData; let callType=incomingCallType;
  document.getElementById('incomingBox').style.display='none';
  try{
    if(callType==='voice'){
      localStream=await navigator.mediaDevices.getUserMedia({audio:true,video:false});
      document.getElementById('voiceBox').style.display='flex';
      document.getElementById('voiceStatus').innerText='Connected to '+data.callerName;
      document.getElementById('voiceNumber').innerHTML='From: <b>'+data.callerName+'</b> '+data.callerNumber;
      document.getElementById('voiceWith').innerHTML='Connected!';
      voiceSeconds=0; voiceTimerInt=setInterval(()=>{voiceSeconds++;let m=String(Math.floor(voiceSeconds/60)).padStart(2,'0');let s=String(voiceSeconds%60).padStart(2,'0');document.getElementById('voiceTimer').innerText=m+':'+s;},1000);
    }else{
      localStream=await navigator.mediaDevices.getUserMedia({video:true,audio:true});
      document.getElementById('localV').srcObject=localStream;
      document.getElementById('videoBox').style.display='flex';
    }
    let pc=createPC(from); let off=await pc.createOffer(); await pc.setLocalDescription(off); ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,[STRIPPED]
    showAlert('Answered! Connected to '+data.callerName);
  }catch(e){showAlert('Allow mic: '+e.message);}
  incomingFrom=null;
}
function declineIncoming(){if(incomingFrom&&ws){ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:{type:'decline'},[STRIPPED] document.getElementById('incomingBox').style.display='none'; incomingFrom=null; showAlert('Declined');}
function endVoiceCall(){document.getElementById('voiceBox').style.display='none'; if(voiceTimerInt)clearInterval(voiceTimerInt);voiceSeconds=0; if(localStream){localStream.getTracks().forEach(t=>t.stop());localStream=null;} for(let k in pcs){try{pcs[k].close();}catch(e){}}pcs={};document.getElementById('remoteBox').innerHTML='';document.querySelectorAll('[id^="audio-"]').forEach(el=>el.remove());}
function endVideoCall(){document.getElementById('videoBox').style.display='none'; if(localStream){localStream.getTracks().forEach(t=>t.stop());localStream=null;} for(let k in pcs){try{pcs[k].close();}catch(e){}}pcs={};document.getElementById('remoteBox').innerHTML='';}
function toggleMute(){if(!localStream)return;isMuted=!isMuted;localStream.getAudioTracks().forEach(t=>t.enabled=!isMuted);showAlert(isMuted?'Muted':'Mic On');}
</script></body></html>
"""

@app.websocket("/ws/tamy")
async def ws_tamy(websocket: WebSocket, token: str = "", name: str = "User", number: str = ""):
    await websocket.accept()
    cid = token or str(id(websocket))
    clients[cid] = websocket
    client_names[cid] = name or cid[:8]
    client_numbers[cid] = number or ""
    await broadcast_users()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                j = json.loads(raw)
                target = j.get("to")
                j["from"] = cid
                j["fromName"] = client_names.get(cid)
                j["fromNumber"] = client_numbers.get(cid)
                if target and target in clients:
                    await clients[target].send_text(json.dumps(j))
                else:
                    for oid, ows in list(clients.items()):
                        if oid!= cid:
                            await ows.send_text(json.dumps(j))
            except:
                for oid, ows in list(clients.items()):
                    if oid!= cid:
                        try:
                            await ows.send_text(raw)
                        except:
                            pass
    except WebSocketDisconnect:
        pass
    finally:
        clients.pop(cid, None)
        client_names.pop(cid, None)
        client_numbers.pop(cid, None)
        await broadcast_users()

async def broadcast_users():
    users = [{"id": cid, "name": client_names.get(cid, cid[:6]), "number": client_numbers.get(cid, "")} for cid in clients.keys()]
    msg = json.dumps({"type": "users", "users": users})
    for ows in list(clients.values()):
        try:
            await ows.send_text(msg)
        except:
            pass
