from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_PAGE = """
<html><head><title>TAMY v3</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:white;text-align:center;font-family:Arial;padding:15px}
.card{background:#1e1e1e;padding:20px;border-radius:15px;border:2px solid #250366;max-width:400px;margin:auto}
button{background:#250366;color:white;padding:14px 25px;border:none;border-radius:10px;font-size:16px;margin:8px;width:90%}
img,video{max-width:100%;border-radius:12px;margin-top:15px;border:2px solid #250366}
input{padding:10px;border-radius:8px;width:90%;margin:10px 0;background:white}
</style></head>
<body>
<h1 style="color:#9c6bff">🌍 TAMY Worldwide</h1>
<p>View Once Photo + Video Opener</p>
<div class="card">
<h3>Upload Any File</h3>
<input type="file" id="file" accept="image/*,video/*"><br>
<button onclick="openFile()">🔓 Open Photo / Video</button>
<button onclick="saveFile()">💾 Save to Phone</button>
<div id="preview"></div>
<br>
<div style="background:gold;padding:10px;border-radius:10px">
<p style="color:black;font-weight:bold;margin:0">Support TAMY ❤️</p>
</div>
</div>
<p style="font-size:11px;margin-top:15px">Created by Calvin Nsamba | TAMY v3 - Photo + Video</p>
<script>
function openFile(){
 const f=document.getElementById('file').files[0];
 if(!f){alert('Select file first!');return;}
 const r=new FileReader();
 r.onload=function(e){
   if(f.type.startsWith('video')){
     document.getElementById('preview').innerHTML='<h4>✅ View Once Video Opened:</h4><video controls autoplay loop src="'+e.target.result+'" id="media"></video>';
   } else {
     document.getElementById('preview').innerHTML='<h4>✅ View Once Photo Opened HD:</h4><img src="'+e.target.result+'" id="media">';
   }
 }
 r.readAsDataURL(f);
}
function saveFile(){
 const m=document.getElementById('media');
 if(!m){alert('Open file first!');return;}
 const a=document.createElement('a');
 a.href=m.src;
 a.download=m.tagName=='VIDEO'?'TAMY-VIDEO.mp4':'TAMY-PHOTO.jpg';
 a.click();
 alert('Saved! Check your gallery!');
}
</script>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/health")
async def health():
    return {"status": "TAMY v3 Photo+Video LIVE"}
