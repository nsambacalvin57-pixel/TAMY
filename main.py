from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_PAGE = """
<html><head><title>TAMY</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:white;text-align:center;font-family:Arial;padding:15px}
.card{background:#1e1e1e;padding:20px;border-radius:15px;border:2px solid #250366;max-width:400px;margin:auto}
button{background:#250366;color:white;padding:14px 25px;border:none;border-radius:10px;font-size:16px;margin:8px;width:90%}
img{max-width:100%;border-radius:12px;margin-top:15px;border:2px solid #250366}
input{padding:10px;border-radius:8px;width:90%;margin:10px 0}
</style></head>
<body>
<h1 style="color:#9c6bff">🌍 TAMY Worldwide</h1>
<p>HD & View Once Opener</p>
<div class="card">
<h3>Upload Photo</h3>
<input type="file" id="file" accept="image/*"><br>
<button onclick="openImage()">🔓 Open / Enhance HD</button>
<button onclick="saveImage()">💾 Save Image</button>
<div id="preview"></div>
</div>
<p style="font-size:12px;margin-top:15px">Created by Calvin Nsamba | TAMY v2.0</p>
<script>
function openImage(){
 const f=document.getElementById('file').files[0];
 if(!f){alert('Select an image first!');return;}
 const r=new FileReader();
 r.onload=function(e){
  document.getElementById('preview').innerHTML='<h4>✅ Opened in HD:</h4><img src="'+e.target.result+'" id="img">';
 }
 r.readAsDataURL(f);
}
function saveImage(){
 const img=document.getElementById('img');
 if(!img){alert('Open an image first!');return;}
 const a=document.createElement('a');
 a.href=img.src; a.download='TAMY-HD.jpg'; a.click();
}
</script>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/health")
async def health():
    return {"status": "TAMY v2 running"}
