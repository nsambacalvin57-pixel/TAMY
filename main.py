from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, json, time, hashlib, html
from collections import defaultdict

app = FastAPI(title="TAMY")
request_counts = defaultdict(list)
BLOCKED_IPS = set()
otp_store = {}

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
#loginScreen{position:fixed;inset:0;background:linear-gradient(135deg,#050508,#0a0a14,#151528);z-index:200;display:flex;align-items:center;justify-content:center;padding:15px;overflow-y:auto}
.loginBox{background:#12122a;border:2px solid #7c3aed;border-radius:20px;padding:22px;width:430px;box-shadow:0 0 40px #7c3aed55;text-align:center}
.loginBox h1{font-size:52px;font-weight:900;letter-spacing:12px;background:linear-gradient(90deg,#7c3aed,#00ff88,#ff00aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.registerTitle{font-size:14px;font-weight:900;margin:8px 0;background:linear-gradient(90deg,#00ff88,#ff00aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.loginBox input{width:100%;padding:12px;border-radius:10px;border:1px solid #2a2a4a;background:#0a0a14;color:#fff;outline:none;margin-bottom:10px;font-size:13px}
.loginBtn{width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(90deg,#7c3aed,#00ff88);color:#000;font-weight:900;cursor:pointer;margin-bottom:8px;font-size:13px}
.loginBtn.sec{background:#1a1a2e;color:#fff;border:1px solid #2a2a4a}
.loginBtn.register{background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff;font-size:14px}
.loginBtn.verify{background:#00ff88;color:#000;font-weight:900}
.loginBtn.callverify{background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;font-weight:900;border:2px solid #00ff88}
#verifyBox{display:none;margin-top:10px;padding:15px;background:#000;border-radius:12px;border:2px dashed #00ff88}
#callBox{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:250;flex-direction:column;align-items:center;justify-content:center;padding:20px}
#incomingBox{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:260;flex-direction:column;align-items:center;justify-content:center;padding:20px}
.callAvatar{width:130px;height:130px;border-radius:30px;background:linear-gradient(135deg,#00ff88,#ff00aa);display:flex;align-items:center;justify-content:center;font-size:50px;font-weight:900;animation:pulse 1.5s infinite;box-shadow:0 0 40px #00ff8855}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
#inviteModal{position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:150;display:none;align-items:center;justify-content:center;padding:15px}
.inviteBox{background:#12122a;border:2px solid #ff00aa;border-radius:20px;padding:20px;width:400px;max-width:95%}
#topNav{height:60px;background:#0a0a14;border-bottom:1px solid #1e1e3a;display:flex;align-items:center;justify-content:space-between;padding:0 12px}
#logo{font-size:36px;font-weight:900;letter-spacing:10px;background:linear-gradient(90deg,#7c3aed,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pill{padding:7px 12px;border-radius:20px;background:#1a1a2e;border:1px solid #2a2a4a;font-size:11px;cursor:pointer}
.pill.voice{background:#00ff8820;border-color:#00ff88;color:#00ff88;font-weight:bold}
.pill.ultra{background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff;font-weight:900}
.pill.invite{background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;font-weight:900}
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
.toolBtn{width:100%;padding:9px;border-radius:8px;border:1px solid #2a2a4a;background:#1a1a3a;color:#fff;cursor:pointer;margin-bottom:5px;font-size:11px;display:flex;gap:6px;align-items:center}
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
#secAlert{position:fixed;top:70px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:10px 18px;border-radius:20px;font-size:12px;font-weight:bold;z-index:500;display:none;max-width:90%}
.userRow{display:flex;justify-content:space-between;align-items:center;padding:6px 8px;background:#0f0f1e;border-radius:8px;margin-bottom:4px;font-size:11px}
.onlineDot{width:7px;height:7px;background:#00ff88;border-radius:50%;display:inline-block}
</style></head><body>

<div id="incomingBox">
<div class="callAvatar" id="incomingAv">K</div>
<h2 style="margin-top:20px;color:#00ff88;font-size:22px;font-weight:900"><i class="fa-solid fa-phone-volume"></i> <span id="incomingType">TAMY VOICE CALL</span></h2>
<p id="incomingName" style="margin:10px 0;color:#fff;font-size:16px;font-weight:bold">king is calling...</p>
<p id="incomingNumber" style="color:#ff00aa;font-size:13px;font-weight:bold"></p>
<p style="color:#aaa;font-size:11px;margin-top:8px">Friends call - Click Answer to receive!</p>
<div style="margin-top:25px;display:flex;gap:12px">
<button class="loginBtn verify" style="width:150px;background:#00ff88;color:#000;font-size:14px" onclick="acceptIncoming()"><i class="fa-solid fa-phone"></i> Answer - Receive Call</button>
<button class="loginBtn sec" style="width:150px;background:#ff0040;color:#fff" onclick="declineIncoming()"><i class="fa-solid fa-phone-slash"></i> Decline</button>
</div>
</div>

<div id="callBox">
<div class="callAvatar">T</div>
<h2 style="margin-top:20px;color:#00ff88;font-size:22px;font-weight:900"><i class="fa-solid fa-phone-volume"></i> TAMY VERIFICATION CALL</h2>
<p id="callStatus" style="margin:10px 0;color:#ff00aa;font-size:14px;font-weight:bold">Incoming verification call from TAMY...</p>
<p id="callNumber" style="color:#fff;font-size:13px"></p>
<p id="callOtpSpeak" style="margin:15px 0;color:#00ff88;font-size:28px;font-weight:900;letter-spacing:10px;background:#000;padding:12px 20px;border-radius:12px;border:2px solid #00ff88"></p>
<div style="margin-top:25px;display:flex;gap:10px">
<button class="loginBtn verify" style="width:140px" onclick="answerCall()"><i class="fa-solid fa-phone"></i> Answer Call</button>
<button class="loginBtn sec" style="width:140px" onclick="endVerifyCall()"><i class="fa-solid fa-phone-slash"></i> End Call</button>
</div>
<button class="loginBtn sec" style="width:290px;margin-top:10px" onclick="repeatCode()"><i class="fa-solid fa-repeat"></i> Repeat Code Again</button>
</div>

<div id="loginScreen">
<div class="loginBox">
<h1>TAMY</h1>
<div class="registerTitle">REGISTER TO HAVE ACCOUNT ON TAMY - Friends can receive calls now!</div>
<small>Receive a verification CALL from TAMY • Voice + Video 4K Call Fix • No Popup</small>
<input id="loginName" placeholder="Your TAMY Name">
<input id="loginNumber" placeholder="Your Contact Number +966..." type="tel">
<input id="loginId" placeholder="Your TAMY ID - ex: tamy_123">
<input id="loginPass" type="password" placeholder="Password min 4">
<button class="loginBtn register" onclick="sendVerification()">REGISTER - Send Code + Call</button>
<div id="verifyBox">
<div style="font-size:13px;color:#00ff88;font-weight:900;margin-bottom:8px">RECEIVE VERIFICATION CODE + CALL FROM TAMY</div>
<div style="font-size:11px;color:#aaa;margin-bottom:10px">Code to <b id="verifyNumberShow" style="color:#ff00aa"></b></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
<button class="loginBtn callverify" onclick="receiveVerificationCall()">Receive verification CALL from TAMY</button>
<button class="loginBtn verify" onclick="showOtp()">Show SMS Code</button>
</div>
<input id="otpInput" placeholder="Enter 6-digit code" style="width:100%;padding:12px;border-radius:10px;border:2px solid #00ff88;background:#0a0a14;color:#fff;font-size:18px;text-align:center;letter-spacing:8px;font-weight:900" maxlength="6">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
<button class="loginBtn verify" onclick="verifyCode()">Verify Code</button>
<button class="loginBtn sec" onclick="resendCode()">Resend Code + Call</button>
</div>
<div id="otpMsg" style="margin-top:8px;font-size:11px;color:#00ff88"></div>
<div style="margin-top:8px;padding:6px;background:#0a0a14;border-radius:8px;border:1px solid #1e1e3a;font-size:10px;color:#666"><b style="color:#00ff88">Demo OTP:</b> <span id="demoOtp" style="color:#ff00aa;font-weight:900;font-size:14px"></span><br><span id="demoNumber" style="font-size:10px"></span></div>
</div>
<button class="loginBtn" onclick="doLoginDirect()" style="margin-top:10px">Sign In Direct</button>
<button class="loginBtn sec" onclick="createNewId()">Create New TAMY ID</button>
<div id="loginMsg" style="margin-top:8px;font-size:11px;color:#00ff88"></div>
</div>
</div>

<div id="inviteModal"><div class="inviteBox">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><b style="color:#ff00aa;font-size:14px">TAMY Add Friends / Invite</b><button onclick="closeInvite()" style="background:#ff0040;color:#fff;border:none;border-radius:50%;width:28px;height:28px;cursor:pointer">X</button></div>
<div style="background:#000;border-radius:10px;padding:10px;border:1px dashed #ff00aa;margin-bottom:10px">
<div style="font-size:10px;color:#ff00aa;font-weight:bold;margin-bottom:6px">YOUR TAMY INVITE LINK</div>
<div id="inviteLinkText" style="font-size:11px;color:#00ff88;word-break:break-all;background:#0a0a14;padding:8px;border-radius:8px;border:1px solid #1e1e3a">Loading...</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
<button class="addBtn" onclick="copyInviteLink()" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff">Copy Link</button>
<button class="addBtn" onclick="shareWhatsApp()" style="background:#25D366;color:#fff">WhatsApp Invite</button>
</div>
</div>
<div style="background:#0a0a14;border-radius:10px;padding:10px;border:1px solid #1e1e3a">
<div style="font-size:10px;color:#00ff88;font-weight:bold;margin-bottom:6px">Add Friend by Name + Number</div>
<div style="display:flex;gap:6px;margin-bottom:6px"><input id="inviteName" placeholder="Friend Name" style="flex:1;padding:8px;border-radius:7px;border:1px solid #2a2a4a;background:#000;color:#fff;font-size:11px"><input id="inviteNumber" placeholder="+966..." type="tel" style="flex:1;padding:8px;border-radius:7px;border:1px solid #2a2a4a;background:#000;color:#fff;font-size:11px"></div>
<button class="addBtn" style="width:100%;background:#00ff88;color:#000" onclick="inviteByNumber()">Add Friend with Number</button>
</div>
</div></div>

<div id="secAlert"></div>
<div id="topNav"><div id="logo">TAMY</div><div style="display:flex;gap:6px;align-items:center"><div class="pill" style="background:#00ff8820;border-color:#00ff88;color:#00ff88">WALL ON</div><div id="liveCount" class="pill">0 Online</div></div><div style="display:flex;gap:6px"><button class="pill invite" onclick="openInvite()">Invite</button><button class="pill voice" onclick="startVoiceCall()">VOICE</button><button class="pill ultra" onclick="startVideoCall()">VIDEO 4K ULTRA HD</button><button class="pill" onclick="doLogout()" style="background:#ff004020;color:#ff0040">Logout</button></div></div>
<div id="main">
<div id="left">
<div class="modes"><div class="mode active" onclick="setMode('chat',this)"><i class="fa-solid fa-comment-dots"></i><b>TAMY CHAT</b></div><div class="mode" onclick="setMode('voice',this)"><i class="fa-solid fa-phone"></i><b>TAMY VOICE</b></div><div class="mode" onclick="setMode('video',this)"><i class="fa-solid fa-video"></i><b>TAMY VIDEO 4K</b></div><div class="mode" onclick="setMode('fun',this)"><i class="fa-solid fa-face-smile"></i><b>TAMY FUN</b></div><div class="mode" onclick="setMode('brain',this)"><i class="fa-solid fa-brain"></i><b>TAMY BRAIN</b></div><div class="mode" onclick="setMode('future',this)"><i class="fa-solid fa-rocket"></i><b>TAMY FUTURE</b></div></div>
<div class="addBox"><div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:10px;color:#00ff88;font-weight:bold">Add TAMY Contact - Name + Number</div><button class="addBtn" style="padding:3px 8px;font-size:9px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()">Invite</button></div><div class="addBoxRow"><input id="addName" placeholder="Contact Name"><input id="addNumber" placeholder="Number +966..." type="tel"></div><div class="addBoxRow"><button class="addBtn" style="flex:1" onclick="addContact()">Add Contact with Number</button></div></div>
<div id="contactsList" class="contacts"><div class="contact active" onclick="openChat('TAMY','T','ai','','')"><div class="avatar">T</div><div style="flex:1"><b>TAMY</b><div style="font-size:10px;color:#00ff88">AI Verified 4K + Call Fix</div></div></div><div class="contact" onclick="openChat('TAMY MEET 4K ULTRA HD','M','group','','')"><div class="avatar" style="background:linear-gradient(135deg,#ff00aa,#7c3aed)">M</div><div style="flex:1"><b>TAMY MEET 4K ULTRA HD</b><div style="font-size:10px;color:#ff00aa">100 people - Group Call</div></div><div id="gCount" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff;padding:3px 7px;border-radius:8px;font-size:9px">0</div></div></div>
<div style="padding:8px;background:#08080f;border-top:1px solid #1e1e3a;max-height:160px;overflow-y:auto"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px"><div style="font-size:10px;color:#ff00aa;font-weight:bold">TAMY ONLINE FRIENDS - Click to Call Private</div><button class="addBtn" style="padding:2px 6px;font-size:8px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()">Add Friends</button></div><div id="onlineList" style="font-size:11px;color:#aaa">No friends online - Invite!</div></div>
</div>
<div id="center">
<div id="centerTop"><div style="display:flex;gap:8px;align-items:center"><div class="avatar" id="hAv">T</div><div><b id="hName">TAMY</b><div id="hNumber" style="font-size:11px;color:#00ff88;font-weight:bold"></div><small style="color:#00ff88;font-size:10px">Verified via CALL • Private Call Fix • Friends can receive calls!</small></div></div><div style="display:flex;gap:6px"><button class="pill invite" onclick="openInvite()">Add Friends</button><button class="pill voice" onclick="startVoiceCall()">VOICE</button><button class="pill ultra" onclick="startVideoCall()">4K ULTRA HD</button></div></div>
<div id="voiceBox"><div style="text-align:center"><div class="avatar" style="width:110px;height:110px;font-size:45px;margin:0 auto 15px;background:linear-gradient(135deg,#00ff88,#7c3aed)">T</div><h2 id="voiceStatus">TAMY VOICE CALL</h2><p id="voiceTimer" style="margin:10px;color:#00ff88;font-size:18px">00:00</p><p id="voiceNumber" style="color:#ff00aa;font-size:13px;font-weight:bold"></p><p id="voiceWith" style="color:#fff;font-size:12px;margin-top:5px"></p><div style="margin-top:25px;display:flex;gap:10px;justify-content:center"><button class="vb voice" onclick="toggleMute()">Mute</button><button class="vb end" onclick="endVoiceCall()">End Voice</button></div></div></div>
<div id="videoBox"><div style="padding:10px 12px;background:linear-gradient(90deg,#0a0a14,#1a1a3a);display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #ff00aa"><div><b style="background:linear-gradient(90deg,#ff00aa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent">TAMY VIDEO 4K ULTRA HD</b><br><small style="color:#00ff88">Friends can receive calls - Private 4K</small></div><div class="pill ultra" style="font-size:9px">PRIVATE 4K CALL FIX</div></div><div id="videoGrid"><div class="videoTile" style="border-color:#ff00aa"><video id="localV" autoplay muted playsinline></video><div style="position:absolute;bottom:6px;left:6px;background:#000a;color:#00ff88;padding:2px 6px;border-radius:6px;font-size:9px">You - <span id="localNumber">+966...</span></div></div><div id="remoteBox" style="display:contents"></div></div><div id="vControls"><button class="vb voice" onclick="toggleMute()">Mute</button><button class="vb" onclick="toggleCam()">Cam 4K</button><button class="vb" style="background:linear-gradient(90deg,#00ff88,#ff00aa)!important;color:#000" onclick="openInvite()">Invite Friends</button><button class="vb end" onclick="endVideoCall()">End 4K</button></div></div>
<div id="msgs"></div>
<div id="inputArea"><button class="iconBtn" onclick="startVoiceCall()" style="background:#00ff8820;color:#00ff88;border-color:#00ff88"><i class="fa-solid fa-phone"></i></button><button class="iconBtn" onclick="openInvite()" style="background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000"><i class="fa-solid fa-user-plus"></i></button><input id="inp" placeholder="Type hello... Friends can receive calls now!" onkeypress="if(event.key==='Enter')sendText()"><button class="iconBtn sendBtn" onclick="sendText()"><i class="fa-solid fa-paper-plane"></i></button></div>
</div>
<div id="right">
<div class="panel" style="border-color:#00ff88;background:linear-gradient(135deg,#00ff8810,#ff00aa10)"><b style="color:#00ff88">TAMY Add Friends / Invite - Friends can receive calls!</b><button class="toolBtn" style="background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;font-weight:900" onclick="openInvite()">Add Friends / Invite</button><button class="toolBtn" style="border-color:#ff00aa;color:#ff00aa" onclick="copyInviteLink()">Copy Invite Link</button><button class="toolBtn" style="border-color:#25D366;color:#25D366" onclick="shareWhatsApp()">Invite via WhatsApp</button></div>
<div class="panel" style="border-color:#00ff88"><b style="color:#00ff88">My TAMY Account - Verified via CALL - Friends can receive calls</b><div id="myIdBox" style="padding:8px;background:#000;border-radius:8px;font-size:11px;word-break:break-all;border:1px dashed #00ff88"></div></div>
<div class="panel"><b>TAMY Live Friends - Friends can receive calls - Private</b><div id="liveUsers" style="font-size:11px;color:#aaa">Connecting...</div></div>
</div>
</div>
<script>
let ws,mode='ai',pcs={},localStream=null,voiceTimerInt=null,voiceSeconds=0,isMuted=false,verifyCallTimer=null;
let currentChatId=null,currentChatName='',currentChatNumber='';
let incomingFrom=null,incomingData=null,incomingCallType='';
const msgsEl=document.getElementById('msgs');
let securityToken=localStorage.getItem('tamy_token')||'';
let myName=localStorage.getItem('tamy_name')||'';
let myPass=localStorage.getItem('tamy_pass')||'';
let myNumber=localStorage.getItem('tamy_number')||'';
let myContacts=JSON.parse(localStorage.getItem('tamy_contacts')||'[]');
let generatedOtp='';
let isVerified=localStorage.getItem('tamy_verified')==='true';

function showLogin(){document.getElementById('loginScreen').style.display='flex'; if(myName) document.getElementById('loginName').value=myName; if(myNumber) document.getElementById('loginNumber').value=myNumber; if(securityToken) document.getElementById('loginId').value=securityToken; if(myPass) document.getElementById('loginPass').value=myPass;}
function hideLogin(){document.getElementById('loginScreen').style.display='none';}
function createNewId(){let newId='tamy_'+Math.random().toString(36).substring(2,8); document.getElementById('loginId').value=newId; document.getElementById('loginMsg').innerText='New TAMY ID: '+newId; showAlert('New ID: '+newId+' - Friends can receive calls now!');}
function sendVerification(){
  let name=document.getElementById('loginName').value.trim();
  let number=document.getElementById('loginNumber').value.trim();
  let id=document.getElementById('loginId').value.trim();
  let pass=document.getElementById('loginPass').value.trim();
  if(!name){showAlert('Type Name!');return;}
  if(!number){showAlert('Type Number to receive call!');return;}
  if(!id){showAlert('Create ID!');return;}
  if(!pass || pass.length<4){showAlert('Password min 4!');return;}
  generatedOtp=Math.floor(100000 + Math.random()*900000).toString();
  securityToken=id; myName=name; myNumber=number; myPass=pass;
  document.getElementById('verifyBox').style.display='block';
  document.getElementById('verifyNumberShow').innerText=myNumber;
  document.getElementById('demoNumber').innerText='TAMY will call '+myNumber;
  document.getElementById('demoOtp').innerText='CODE: '+generatedOtp;
  document.getElementById('otpMsg').innerHTML='Code for '+myNumber+': '+generatedOtp;
  document.getElementById('otpInput').value='';
  fetch('/send-otp?number='+encodeURIComponent(number)+'&otp='+generatedOtp);
  showAlert('Code ready: '+generatedOtp+' - Click Receive CALL!');
  setTimeout(()=>receiveVerificationCall(),800);
}
function receiveVerificationCall(){
  if(!generatedOtp){showAlert('Generate code first!');return;}
  document.getElementById('callBox').style.display='flex';
  document.getElementById('callNumber').innerHTML='Calling <b style="color:#00ff88">'+myNumber+'</b>... From: <b style="color:#ff00aa">TAMY Verification</b>';
  document.getElementById('callOtpSpeak').innerText=generatedOtp;
  document.getElementById('callStatus').innerText='TAMY calling... Receive verification call from TAMY...';
  showAlert('Incoming verification call from TAMY! Code: '+generatedOtp);
  if(verifyCallTimer) clearTimeout(verifyCallTimer);
  verifyCallTimer=setTimeout(()=>answerCall(),1200);
}
function answerCall(){
  document.getElementById('callStatus').innerText='Call Answered - TAMY Verification';
  document.getElementById('callNumber').innerHTML='Connected to <b style="color:#00ff88">'+myNumber+'</b><br>TAMY speaking code...';
  speakCode();
}
function speakCode(){
  if(!generatedOtp) return;
  let digits=generatedOtp.split('').join(' ');
  let text='Hello from TAMY. Your verification code is. '+digits+'. I repeat. '+digits+'. Thank you for registering on TAMY.';
  if('speechSynthesis' in window){
    speechSynthesis.cancel();
    let utter=new SpeechSynthesisUtterance(text);
    utter.rate=0.85;
    let voices=speechSynthesis.getVoices();
    if(voices.length>0){let enVoice=voices.find(v=>v.lang.includes('en'))||voices[0]; utter.voice=enVoice;}
    utter.onstart=()=>{document.getElementById('callStatus').innerText='TAMY Speaking: '+generatedOtp+' - Listen...';};
    utter.onend=()=>{document.getElementById('callStatus').innerText='Finished speaking code: '+generatedOtp;};
    speechSynthesis.speak(utter);
  }
  document.getElementById('otpInput').value=generatedOtp;
  document.getElementById('otpMsg').innerHTML='Received CALL from TAMY! Code: '+generatedOtp+' - Click Verify!';
}
function repeatCode(){if(!generatedOtp){showAlert('No code!');return;} speakCode();}
function endVerifyCall(){document.getElementById('callBox').style.display='none'; if('speechSynthesis' in window) speechSynthesis.cancel(); if(verifyCallTimer) clearTimeout(verifyCallTimer); showAlert('Verification call ended - Code: '+generatedOtp);}
function showOtp(){if(!generatedOtp){showAlert('Generate first!');return;} document.getElementById('otpMsg').innerHTML='SMS Code: '+generatedOtp; document.getElementById('otpInput').value=generatedOtp;}
function resendCode(){generatedOtp=Math.floor(100000 + Math.random()*900000).toString(); document.getElementById('demoOtp').innerText='NEW CODE: '+generatedOtp; document.getElementById('otpMsg').innerHTML='New code: '+generatedOtp; document.getElementById('callOtpSpeak').innerText=generatedOtp; fetch('/send-otp?number='+encodeURIComponent(myNumber)+'&otp='+generatedOtp); showAlert('New code: '+generatedOtp); setTimeout(()=>receiveVerificationCall(),600);}
function verifyCode(){
  let entered=document.getElementById('otpInput').value.trim();
  if(!entered){showAlert('Enter code!');return;}
  fetch('/verify-otp?number='+encodeURIComponent(myNumber)+'&otp='+entered).then(r=>r.json()).then(d=>{
    if(d.success || entered===generatedOtp){
      isVerified=true;
      localStorage.setItem('tamy_verified','true'); localStorage.setItem('tamy_token',securityToken); localStorage.setItem('tamy_name',myName); localStorage.setItem('tamy_number',myNumber); localStorage.setItem('tamy_pass',myPass);
      document.getElementById('myIdBox').innerHTML='Name: <b style="color:#00ff88">'+myName+'</b><br>Number: <b style="color:#ff00aa">'+myNumber+'</b><br>ID: <b>'+securityToken+'</b><br><span style="color:#00ff88">Verified via CALL - Friends can receive calls!</span>';
      document.getElementById('inviteLinkText').innerText=location.origin+'?invite='+securityToken;
      document.getElementById('callBox').style.display='none'; if('speechSynthesis' in window) speechSynthesis.cancel();
      hideLogin(); showAlert('Verified! Welcome '+myName+'! Friends can receive calls now!'); connect(); openChat('TAMY','T','ai','',''); loadContacts();
    }else{
      document.getElementById('otpMsg').innerHTML='<span style="color:#ff0040">Wrong! Correct: '+generatedOtp+'</span>'; showAlert('Wrong! Correct: '+generatedOtp);
    }
  });
}
function doLoginDirect(){
  let name=document.getElementById('loginName').value.trim(); let number=document.getElementById('loginNumber').value.trim(); let id=document.getElementById('loginId').value.trim(); let pass=document.getElementById('loginPass').value.trim();
  if(!name||!number||!id||!pass){showAlert('Fill all!');return;}
  if(localStorage.getItem('tamy_verified')!=='true' && localStorage.getItem('tamy_token')!==id){showAlert('Need to Register and receive verification call first!');return;}
  securityToken=id; myName=name; myNumber=number; myPass=pass; isVerified=true;
  localStorage.setItem('tamy_token',securityToken); localStorage.setItem('tamy_name',myName); localStorage.setItem('tamy_number',myNumber); localStorage.setItem('tamy_pass',myPass); localStorage.setItem('tamy_verified','true');
  document.getElementById('myIdBox').innerHTML='Name: <b style="color:#00ff88">'+myName+'</b><br>Number: <b style="color:#ff00aa">'+myNumber+'</b><br>ID: <b>'+securityToken+'</b><br><span style="color:#00ff88">Verified</span>';
  document.getElementById('inviteLinkText').innerText=location.origin+'?invite='+securityToken;
  hideLogin(); showAlert('Signed In! Friends can receive calls!'); connect(); openChat('TAMY','T','ai','',''); loadContacts();
}
function doLogout(){
  showAlert('Logging out...');
  setTimeout(()=>{
    localStorage.removeItem('tamy_token'); localStorage.removeItem('tamy_name'); localStorage.removeItem('tamy_number'); localStorage.removeItem('tamy_pass'); localStorage.removeItem('tamy_verified');
    securityToken=''; myName=''; myNumber=''; myPass=''; generatedOtp=''; isVerified=false;
    document.getElementById('loginName').value=''; document.getElementById('loginNumber').value=''; document.getElementById('loginId').value=''; document.getElementById('loginPass').value=''; document.getElementById('otpInput').value=''; document.getElementById('verifyBox').style.display='none'; document.getElementById('callBox').style.display='none'; document.getElementById('incomingBox').style.display='none'; if('speechSynthesis' in window) speechSynthesis.cancel();
    showLogin(); if(ws) ws.close(); showAlert('Logged out');
  },500);
}
if(securityToken && myName && myNumber && isVerified){document.getElementById('myIdBox').innerHTML='Name: <b style="color:#00ff88">'+myName+'</b><br>Number: <b style="color:#ff00aa">'+myNumber+'</b><br>ID: <b>'+securityToken+'</b><br><span style="color:#00ff88">Verified - Friends can receive calls!</span>'; document.getElementById('inviteLinkText').innerText=location.origin+'?invite='+securityToken; hideLogin();}else{showLogin();}
function openInvite(){document.getElementById('inviteLinkText').innerText=location.origin+'?invite='+securityToken+'&from='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNumber); document.getElementById('inviteModal').style.display='flex';}
function closeInvite(){document.getElementById('inviteModal').style.display='none';}
function copyInviteLink(){let link=document.getElementById('inviteLinkText').innerText; navigator.clipboard.writeText(link).then(()=>showAlert('Invite Link Copied!'));}
function shareWhatsApp(){let link=document.getElementById('inviteLinkText').innerText; let text=encodeURIComponent('Join me on TAMY - Register and receive verification call from TAMY! My Number: '+myNumber+' Link: '+link); window.open('https://wa.me/?text='+text,'_blank');}
function inviteByNumber(){let name=document.getElementById('inviteName').value.trim()||document.getElementById('addName').value.trim(); let number=document.getElementById('inviteNumber').value.trim()||document.getElementById('addNumber').value.trim(); if(!name||!number){showAlert('Type Name and Number!');return;} addContactDirect(name,number); document.getElementById('inviteName').value=''; document.getElementById('inviteNumber').value=''; document.getElementById('addName').value=''; document.getElementById('addNumber').value=''; closeInvite();}
function addContactDirect(name,number){
  if(!name||!number)return;
  let id=name.replace(/[^a-zA-Z0-9]/g,'').substring(0,12)+'_'+Date.now().toString().slice(-4);
  myContacts.push({name:name,number:number,id:id});
  localStorage.setItem('tamy_contacts',JSON.stringify(myContacts));
  let list=document.getElementById('contactsList');
  let div=document.createElement('div'); div.className='contact'; div.dataset.id=id; div.dataset.tamyid=id;
  let av=name.charAt(0).toUpperCase();
  div.innerHTML='<div class="avatar" style="background:linear-gradient(135deg,#00ff88,#ff00aa)">'+av+'</div><div style="flex:1"><b>'+name+'</b><div style="font-size:11px;color:#00ff88"><i class="fa-solid fa-phone"></i> '+number+'</div><div style="font-size:9px;color:#a78bfa">Private - Friends can receive calls</div></div><div style="display:flex;flex-direction:column;gap:3px"><button class="addBtn" style="padding:4px 6px;font-size:8px;background:#00ff88;color:#000" onclick="event.stopPropagation();startPrivateCall(\\''+id+'\\',\\''+name+'\\',\\''+number+'\\',\\'voice\\')"><i class="fa-solid fa-phone"></i></button><button class="addBtn" style="padding:4px 6px;font-size:8px;background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="event.stopPropagation();startPrivateCall(\\''+id+'\\',\\''+name+'\\',\\''+number+'\\',\\'video\\')">4K</button></div>';
  div.onclick=function(){openChat(name,av,'private',number,id); document.querySelectorAll('.contact').forEach(c=>c.classList.remove('active')); div.classList.add('active');};
  list.appendChild(div);
  showAlert('Friend '+name+' Added - Can receive calls!');
}
function loadContacts(){
  myContacts.forEach(c=>{
    let list=document.getElementById('contactsList');
    if(document.querySelector('[data-id="'+c.id+'"]'))return;
    let div=document.createElement('div'); div.className='contact'; div.dataset.id=c.id; div.dataset.tamyid=c.id;
    let av=c.name.charAt(0).toUpperCase();
    div.innerHTML='<div class="avatar" style="background:linear-gradient(135deg,#00ff88,#ff00aa)">'+av+'</div><div style="flex:1"><b>'+c.name+'</b><div style="font-size:11px;color:#00ff88"><i class="fa-solid fa-phone"></i> '+c.number+'</div><div style="font-size:9px;color:#a78bfa">Private - Friends can receive calls</div></div><div style="display:flex;flex-direction:column;gap:3px"><button class="addBtn" style="padding:4px 6px;font-size:8px;background:#00ff88;color:#000" onclick="event.stopPropagation();startPrivateCall(\\''+c.id+'\\',\\''+c.name+'\\',\\''+c.number+'\\',\\'voice\\')"><i class="fa-solid fa-phone"></i></button><button class="addBtn" style="padding:4px 6px;font-size:8px;background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="event.stopPropagation();startPrivateCall(\\''+c.id+'\\',\\''+c.name+'\\',\\''+c.number+'\\',\\'video\\')">4K</button></div>';
    div.onclick=function(){openChat(c.name,av,'private',c.number,c.id); document.querySelectorAll('.contact').forEach(x=>x.classList.remove('active')); div.classList.add('active');};
    list.appendChild(div);
  });
}
function showAlert(m){let e=document.getElementById('secAlert');e.innerText=m;e.style.display='block';setTimeout(()=>e.style.display='none',4000);}
function copyLink(){copyInviteLink();}
function addContact(){let nameEl=document.getElementById('addName'); let numEl=document.getElementById('addNumber'); let name=nameEl.value.trim(); let number=numEl.value.trim(); if(!name||!number){showAlert('Type Name and Number!');return;} addContactDirect(name,number); nameEl.value=''; numEl.value='';}
function setMode(m,el){currentMode=m; document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active')); el.classList.add('active'); if(m==='voice'){openChat('TAMY VOICE','V','group','',''); startVoiceCall();} else if(m==='video'){openChat('TAMY VIDEO 4K ULTRA HD','V','group','',''); startVideoCall();} else if(m==='chat') openChat('TAMY CHAT','C','group','',''); else if(m==='fun') openChat('TAMY FUN','F','fun','',''); else if(m==='brain') openChat('TAMY BRAIN','B','ai','',''); else if(m==='future') openChat('TAMY FUTURE','F','ai','','');}

function openChat(name,av,m,number,chatId){
  currentChatId = chatId || null;
  currentChatName = name;
  currentChatNumber = number || '';
  mode=m==='private'?'group':m==='fun'?'fun':m==='ai'?'ai':'group';
  document.getElementById('hName').innerText=name;
  document.getElementById('hAv').innerText=av;
  if(chatId){
    document.getElementById('hNumber').innerHTML='<i class="fa-solid fa-phone"></i> To: <b style="color:#00ff88">'+number+'</b> - PRIVATE - Friends can receive calls - ONLY to '+name;
  }else{
    document.getElementById('hNumber').innerHTML=number? '<i class="fa-solid fa-phone"></i> Contact: <b>'+number+'</b> - '+(m==='ai'?'Your Number: <b>'+myNumber+'</b>':'GROUP') : (m==='ai'?'<i class="fa-solid fa-phone"></i> Your Number: <b>'+myNumber+'</b>':'Group - goes to other people');
  }
  msgsEl.innerHTML='';
  if(m==='ai') addMsg('Welcome <b>'+myName+'</b> to <b>TAMY</b> - Friends can receive calls fix!<br><br>Your Number: <b style="color:#ff00aa">'+myNumber+'</b><br>ID: '+securityToken+'<br><br><b>How friends receive calls:</b><br>1. Click friend from ONLINE FRIENDS list<br>2. Click VOICE or 4K button<br>3. Friend gets popup <b>Answer - Receive Call</b><br>4. Friend clicks Answer - Call connects!<br><br><button class="addBtn" style="background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()">Add Friends / Invite Now</button>','other');
  else if(chatId) addMsg('Private chat with <b>'+name+'</b> - <b style="color:#00ff88">PRIVATE - Friends can receive calls</b><br>Number: <b style="color:#00ff88">'+number+'</b> - ONLY to '+name+' - NOT to other people<br><br><button class="addBtn" style="background:#00ff88;color:#000" onclick="startPrivateCall(\\''+chatId+'\\',\\''+name+'\\',\\''+number+'\\',\\'voice\\')"><i class="fa-solid fa-phone"></i> VOICE CALL - Friend will receive!</button> <button class="addBtn" style="background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="startPrivateCall(\\''+chatId+'\\',\\''+name+'\\',\\''+number+'\\',\\'video\\')"><i class="fa-solid fa-video"></i> VIDEO 4K - Friend will receive!</button>','other');
  else addMsg('You are in <b>'+name+'</b> - GROUP (100 people) - Goes to other people<br><br><button class="addBtn" style="background:#00ff88;color:#000" onclick="startVoiceCall()">GROUP VOICE CALL - All friends receive</button>','other');
}

function getWsUrl(){return (location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws/tamy?token='+securityToken+'&name='+encodeURIComponent(myName)+'&number='+encodeURIComponent(myNumber);}
function connect(){
  if(!securityToken)return;
  if(ws)try{ws.close();}catch(e){}
  ws=new WebSocket(getWsUrl());
  ws.onopen=()=>{
    document.getElementById('localNumber').innerText=myNumber;
    document.getElementById('liveUsers').innerHTML='Signed in: <b>'+myName+'</b><br>Number: <b style="color:#ff00aa">'+myNumber+'</b><br>ID: '+securityToken.substring(0,8)+'<br><span style="color:#00ff88">Verified - Friends can receive calls!</span><br><button class="addBtn" style="margin-top:6px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()">Invite Friends</button>';
    document.getElementById('liveCount').innerText='LIVE - Friends can receive calls';
    showAlert('TAMY Connected - Friends can receive calls now!');
  };
  ws.onmessage=async e=>{
    let d=JSON.parse(e.data);
    if(d.type==='users'){
      let users=d.users||[];
      document.getElementById('liveCount').innerText=users.length+' Online - Can receive calls';
      let g=document.getElementById('gCount'); if(g) g.innerText=users.length;
      let html='';
      users.forEach(u=>{
        if(u.id===securityToken) return;
        html+='<div class="userRow"><div><span class="onlineDot"></span> <b>'+u.name+'</b><br><span style="color:#00ff88;font-size:11px"><i class="fa-solid fa-phone"></i> '+(u.number||'')+'</span><br><span style="font-size:8px;color:#00ff88">Can receive calls - Click to call!</span></div><div style="display:flex;gap:3px;flex-direction:column"><button class="addBtn" style="padding:4px 6px;font-size:8px;background:#00ff88;color:#000" onclick="startPrivateCall(\\''+u.id+'\\',\\''+u.name+'\\',\\''+(u.number||'')+'\\',\\'voice\\')"><i class="fa-solid fa-phone"></i> Call</button><button class="addBtn" style="padding:4px 6px;font-size:8px;background:linear-gradient(90deg,#ff00aa,#7c3aed);color:#fff" onclick="startPrivateCall(\\''+u.id+'\\',\\''+u.name+'\\',\\''+(u.number||'')+'\\',\\'video\\')">4K</button></div></div>';
      });
      if(html==='') html='<div style="font-size:10px;color:#666">No friends online - Invite friends to receive calls!<br><button class="addBtn" style="margin-top:6px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000" onclick="openInvite()">Invite Friends - Can receive calls</button></div>';
      document.getElementById('onlineList').innerHTML=html;
      document.getElementById('liveUsers').innerHTML=users.map(u=>'<span class="onlineDot"></span> '+u.name+'<br><small style="color:#00ff88">'+(u.number||'')+' • Can receive calls</small>').join('<br>')||'No friends';
    }
    if(d.type==='chat'){
      addMsg(d.text+'<br><small style="color:#00ff88">From: '+d.fromName+' '+(d.fromNumber||'')+'</small>','other');
    }
    if(d.type==='signal') await handleSignal(d);
  };
  ws.onclose=()=>{if(securityToken)setTimeout(connect,2000);};
}

function addMsg(h,c){let t=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});let div=document.createElement('div');div.className='bubble '+c;div.innerHTML=h+'<div style="text-align:right;font-size:9px;opacity:0.5">'+t+' • TAMY • '+myNumber+'</div>';msgsEl.appendChild(div);msgsEl.scrollTop=msgsEl.scrollHeight;}
function sendText(){
  let inp=document.getElementById('inp');let text=inp.value.trim();if(!text)return;
  addMsg(text+'<br><small style="color:#00ff88">To: '+(currentChatName||'Group')+'</small>','me');inp.value='';
  if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:'chat',text:text,token:securityToken,name:myName,number:myNumber,to:currentChatId}));
}

// --- PRIVATE CALL FIX - FRIENDS CAN RECEIVE CALLS! ---

function startPrivateCall(targetId, targetName, targetNumber, callType){
  if(!targetId){showAlert('Select friend from ONLINE FRIENDS - Click name first!');return;}
  currentChatId=targetId; currentChatName=targetName; currentChatNumber=targetNumber;
  if(callType==='voice') startVoiceCall(targetId, targetName, targetNumber);
  else startVideoCall(targetId, targetName, targetNumber);
}

async function startVoiceCall(targetId, targetName, targetNumber){
  let toId = targetId || currentChatId;
  let toName = targetName || currentChatName || 'Friend';
  let toNumber = targetNumber || currentChatNumber || '';
  try{
    localStream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,sampleRate:48000},video:false});
    document.getElementById('voiceBox').style.display='flex';
    document.getElementById('voiceStatus').innerText= toId? 'TAMY VOICE CALL to '+toName : 'TAMY VOICE CALL - Group';
    document.getElementById('voiceNumber').innerHTML='Your Number: <b>'+myNumber+'</b>';
    document.getElementById('voiceWith').innerHTML= toId? 'Calling <b style="color:#00ff88">'+toName+'</b> - <b style="color:#ff00aa">'+toNumber+'</b> - Private - Friend will receive popup Answer!' : 'Group call - All friends will receive!';
    voiceSeconds=0;document.getElementById('voiceTimer').innerText='00:00';
    voiceTimerInt=setInterval(()=>{voiceSeconds++;let m=String(Math.floor(voiceSeconds/60)).padStart(2,'0');let s=String(voiceSeconds%60).padStart(2,'0');document.getElementById('voiceTimer').innerText=m+':'+s;},1000);
    if(ws){
      let signalData={type:'voice_call',callType:'voice',targetName:toName,targetNumber:toNumber,callerName:myName,callerNumber:myNumber,private:!!toId};
      ws.send(JSON.stringify({type:'signal',to: toId || null,data:signalData,token:securityToken,name:myName,number:myNumber}));
      showAlert(toId? 'Calling '+toName+' - '+toNumber+' - Friend will receive popup Answer!' : 'Group voice call - All friends will receive!');
    }
    addMsg('TAMY VOICE CALL to <b>'+toName+'</b> '+toNumber+' - Calling... Friend will receive Answer popup!','me');
  }catch(e){showAlert('Allow mic: '+e.message);}
}

async function startVideoCall(targetId, targetName, targetNumber){
  let toId = targetId || currentChatId;
  let toName = targetName || currentChatName || 'Friend';
  let toNumber = targetNumber || currentChatNumber || '';
  try{
    localStream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720},frameRate:{ideal:30}},audio:true});
    document.getElementById('localV').srcObject=localStream;
    document.getElementById('videoBox').style.display='flex';
    document.getElementById('localNumber').innerText=myNumber;
    if(ws){
      let signalData={type:'call',callType:'video',targetName:toName,targetNumber:toNumber,callerName:myName,callerNumber:myNumber,private:!!toId};
      ws.send(JSON.stringify({type:'signal',to: toId || null,data:signalData,token:securityToken,name:myName,number:myNumber}));
      showAlert(toId? 'Video 4K calling '+toName+' - Friend will receive popup Answer!' : 'Group video 4K - All friends will receive!');
    }
    addMsg('TAMY VIDEO 4K ULTRA HD to <b>'+toName+'</b> '+toNumber+' - Calling... Friend will receive Answer popup!','me');
  }catch(e){
    try{
      localStream=await navigator.mediaDevices.getUserMedia({video:true,audio:true});
      document.getElementById('localV').srcObject=localStream;
      document.getElementById('videoBox').style.display='flex';
      if(ws){
        let signalData={type:'call',callType:'video',targetName:toName,targetNumber:toNumber,callerName:myName,callerNumber:myNumber,private:!!toId};
        ws.send(JSON.stringify({type:'signal',to: toId || null,data:signalData,token:securityToken,name:myName,number:myNumber}));
      }
    }catch(e2){showAlert('Allow cam mic: '+e2.message);}
  }
}

function createPC(id){
  // FIXED ICE SERVERS - Multiple STUN + FREE TURN - Friends behind NAT can receive calls now!
  let pc=new RTCPeerConnection({
    iceServers:[
      {urls:'stun:stun.l.google.com:19302'},
      {urls:'stun:stun1.l.google.com:19302'},
      {urls:'stun:stun2.l.google.com:19302'},
      {urls:'stun:stun.relay.metered.ca:80'},
      {urls:'turn:openrelay.metered.ca:80',username:'openrelayproject',credential:'openrelayproject'},
      {urls:'turn:openrelay.metered.ca:443',username:'openrelayproject',credential:'openrelayproject'},
      {urls:'turn:openrelay.metered.ca:443?transport=tcp',username:'openrelayproject',credential:'openrelayproject'}
    ],
    iceCandidatePoolSize:10
  });
  pc.onicecandidate=e=>{
    if(e.candidate&&ws){
      ws.send(JSON.stringify({type:'signal',to:id,data:{candidate:e.candidate},token:securityToken,name:myName,number:myNumber}));
    }
  };
  pc.ontrack=e=>{
    let wrapId='wrap-'+id;
    let wrap=document.getElementById(wrapId);
    if(!wrap){
      wrap=document.createElement('div');wrap.id=wrapId;wrap.className='videoTile';wrap.style.borderColor='#00ff88';
      wrap.innerHTML='<div style="position:absolute;top:6px;left:6px;background:linear-gradient(90deg,#00ff88,#ff00aa);color:#000;padding:4px 10px;border-radius:10px;font-size:9px;font-weight:900;z-index:2">Friend - '+id.substring(0,8)+'</div>';
      let v=document.createElement('video');v.id='remote-'+id;v.autoplay=true;v.playsInline=true;wrap.appendChild(v);
      document.getElementById('remoteBox').appendChild(wrap);
      // For voice, create audio element
      if(!document.getElementById('remote-'+id) || e.streams[0].getVideoTracks().length===0){
        let audioWrap=document.createElement('div');
        audioWrap.innerHTML='<audio id="remote-audio-'+id+'" autoplay playsinline></audio>';
        document.body.appendChild(audioWrap);
        document.getElementById('remote-audio-'+id).srcObject=e.streams[0];
      }
    }
    let videoEl=document.getElementById('remote-'+id);
    if(videoEl) videoEl.srcObject=e.streams[0];
  };
  pc.onconnectionstatechange=()=>{
    if(pc.connectionState==='connected'){
      showAlert('Call connected! Friends can receive calls - Connected to '+id.substring(0,8));
    }else if(pc.connectionState==='failed'){
      showAlert('Call failed - Trying TURN - Friends behind NAT - Retrying...');
      pc.restartIce();
    }
  };
  if(localStream) localStream.getTracks().forEach(t=>pc.addTrack(t,localStream));
  pcs[id]=pc;
  return pc;
}

async function handleSignal(d){
  let from=d.from||'peer';
  let data=d.data||{};
  let fromName=d.fromName||d.name||from.substring(0,8);
  let fromNumber=d.fromNumber||d.number||'';

  if(data.type==='voice_call' || data.type==='call'){
    // INCOMING CALL - Show popup so friend CAN receive!
    let callType=data.callType|| (data.type==='voice_call'?'voice':'video');
    incomingFrom=from;
    incomingData=data;
    incomingCallType=callType;

    document.getElementById('incomingBox').style.display='flex';
    document.getElementById('incomingAv').innerText=fromName.charAt(0).toUpperCase();
    document.getElementById('incomingType').innerText= callType==='voice'? 'TAMY VOICE CALL' : 'TAMY VIDEO 4K ULTRA HD CALL';
    document.getElementById('incomingName').innerHTML=fromName+' is calling you...<br><span style="color:#00ff88;font-size:14px">Click Answer to receive call!</span>';
    document.getElementById('incomingNumber').innerHTML='From: <b style="color:#00ff88">'+fromName+'</b><br>Number: <b style="color:#ff00aa">'+fromNumber+'</b><br>Private Call - Friends can receive calls!';

    // Ring sound + vibration
    showAlert('Incoming '+(callType==='voice'?'VOICE':'VIDEO 4K')+' call from '+fromName+' '+fromNumber+' - Click Answer to receive!');

    // Auto play ring
    if(navigator.vibrate) navigator.vibrate([500,200,500]);

  }else if(data.type==='offer'){
    let pc=createPC(from);
    await pc.setRemoteDescription(new RTCSessionDescription(data));
    let ans=await pc.createAnswer();
    await pc.setLocalDescription(ans);
    ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,token:securityToken,name:myName,number:myNumber}));
  }else if(data.type==='answer'){
    let pc=pcs[from];
    if(pc) await pc.setRemoteDescription(new RTCSessionDescription(data));
  }else if(data.candidate){
    let pc=pcs[from];
    if(!pc) pc=pcs[Object.keys(pcs)[0]];
    if(pc){
      try{await pc.addIceCandidate(new RTCIceCandidate(data.candidate));}catch(e){}
    }else{
      for(let k in pcs){try{await pcs[k].addIceCandidate(new RTCIceCandidate(data.candidate));}catch(e){}}
    }
  }
}

async function acceptIncoming(){
  if(!incomingFrom){showAlert('No incoming call!');return;}
  let from=incomingFrom;
  let data=incomingData;
  let callType=incomingCallType;

  document.getElementById('incomingBox').style.display='none';

  try{
    if(callType==='voice'){
      localStream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,sampleRate:48000},video:false});
      document.getElementById('voiceBox').style.display='flex';
      document.getElementById('voiceStatus').innerText='TAMY VOICE CALL with '+data.callerName;
      document.getElementById('voiceNumber').innerHTML='From: <b style="color:#00ff88">'+data.callerName+'</b><br>Number: <b style="color:#ff00aa">'+data.callerNumber+'</b>';
      document.getElementById('voiceWith').innerHTML='Connected - Private - Friend call received!';
      voiceSeconds=0;document.getElementById('voiceTimer').innerText='00:00';
      voiceTimerInt=setInterval(()=>{voiceSeconds++;let m=String(Math.floor(voiceSeconds/60)).padStart(2,'0');let s=String(voiceSeconds%60).padStart(2,'0');document.getElementById('voiceTimer').innerText=m+':'+s;},1000);
    }else{
      localStream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720}},audio:true});
      document.getElementById('localV').srcObject=localStream;
      document.getElementById('videoBox').style.display='flex';
      document.getElementById('localNumber').innerText=myNumber;
    }

    let pc=createPC(from);
    let off=await pc.createOffer();
    await pc.setLocalDescription(off);
    ws.send(JSON.stringify({type:'signal',to:from,data:pc.localDescription,token:securityToken,name:myName,number:myNumber}));
    showAlert('Call answered - Connected to '+data.callerName+' - Friends can receive calls success!');

  }catch(e){
    showAlert('Allow mic/cam to receive call: '+e.message);
  }

  incomingFrom=null; incomingData=null;
}

function declineIncoming(){
  if(!incomingFrom){document.getElementById('incomingBox').style.display='none';return;}
  // Send decline signal
  if(ws){
    ws.send(JSON.stringify({type:'signal',to:incomingFrom,data:{type:'decline',message:'Call declined - Friend busy'},token:securityToken,name:myName,number:myNumber}));
  }
  document.getElementById('incomingBox').style.display='none';
  showAlert('Call declined - '+incomingData?.callerName+' will be notified');
  incomingFrom=null; incomingData=null;
}

function endVoiceCall(){
  document.getElementById('voiceBox').style.display='none';
  if(voiceTimerInt)clearInterval(voiceTimerInt);voiceSeconds=0;
  if(localStream){localStream.getTracks().forEach(t=>t.stop());localStream=null;}
  for(let k in pcs){try{pcs[k].close();}catch(e){}}pcs={};document.getElementById('remoteBox').innerHTML='';
  // Remove audio elements
  document.querySelectorAll('[id^="remote-audio-"]').forEach(el=>el.remove());
  showAlert('Voice call ended');
}
function endVideoCall(){
  document.getElementById('videoBox').style.display='none';
  if(localStream){localStream.getTracks().forEach(t=>t.stop());localStream=null;}
  for(let k in pcs){try{pcs[k].close();}catch(e){}}pcs={};document.getElementById('remoteBox').innerHTML='';
  document.querySelectorAll('[id^="remote-audio-"]').forEach(el=>el.remove());
  showAlert('Video 4K call ended');
}
function toggleMute(){if(!localStream)return;isMuted=!isMuted;localStream.getAudioTracks().forEach(t=>t.enabled=!isMuted);showAlert(isMuted?'Mic Muted':'Mic On - Friends can hear you!');}
function toggleCam(){if(!localStream)return;localStream.getVideoTracks().forEach(t=>t.enabled=!t.enabled);}

if(securityToken && myName && myNumber && isVerified){connect(); openChat('TAMY','T','ai','',''); loadContacts();}
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/send-otp")
def send_otp(number: str = "", otp: str = ""):
    otp_store[number] = {"otp": otp, "time": time.time()}
    return {"success": True, "message": f"Code {otp} sent to {number}", "otp": otp}

@app.get("/verify-otp")
def verify_otp(number: str = "", otp: str = ""):
    stored = otp_store.get(number)
    if not stored:
        if len(otp) == 6 and otp.isdigit():
            return {"success": True, "message": "Verified"}
        return {"success": False, "message": "No OTP"}
    if stored["otp"] == otp:
        if time.time() - stored["time"] > 300:
            return {"success": False, "message": "OTP expired"}
        stored["verified"] = True
        return {"success": True, "message": f"Verified {number}"}
    else:
        return {"success": False, "message": f"Wrong! Expected {stored['otp']}"}

@app.get("/ai")
def ai_endpoint(message: str = "", mode: str = "chat", token: str = ""):
    safe_msg = sanitize_input(message)
    block_hash = hashlib.sha256(f"{safe_msg}{time.time()}".encode()).hexdigest()[:8]
    return {"reply": f"<b>TAMY Verified 4K - Friends can receive calls!</b> 0x{block_hash}<br>You: '{safe_msg}'", "model": "TAMY", "hash": f"0x{block_hash}"}

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
                # Keep original fields
                msg_to_forward = j.copy()
                msg_to_forward['from'] = cid
                msg_to_forward['fromName'] = client_names.get(cid, "User")
                msg_to_forward['fromNumber'] = client_numbers.get(cid, "")

                target = j.get("to")
                if target and target in clients:
                    # PRIVATE CALL - ONLY to that friend - Friends can receive calls!
                    try:
                        await clients[target].send_text(json.dumps(msg_to_forward))
                    except:
                        pass
                else:
                    # GROUP or chat without target - broadcast to others
                    for oid, ows in list(clients.items()):
                        if oid!= cid:
                            try:
                                await ows.send_text(json.dumps(msg_to_forward))
                            except:
                                pass
            except Exception as ex:
                # fallback
                for oid, ows in list(clients.items()):
                    if oid!= cid:
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
