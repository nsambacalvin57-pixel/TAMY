from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>TAMY Worldwide</title>
    <style>
    body { background: #0a0a0a; color: white; text-align: center; font-family: Arial; padding: 50px; }
    h1 { color: #25D366; font-size: 50px; }
    .box { background: #1a1a1a; padding: 30px; border-radius: 20px; margin: 20px; border: 2px solid #25D366; }
    button { background: #25D366; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-size: 18px; cursor: pointer; }
    </style>
    </head>
    <body>
    <h1>🌍 TAMY Worldwide</h1>
    <h2>TAMY & View Once Opener</h2>
    <div class="box">
    <h3>✅ TAMY is LIVE!</h3>
    <p>Your worldwide app is running successfully!</p>
    <p>Repository: nsambacalvin57-pixel/TAMY</p>
    <button onclick="alert('TAMY Ready for Render Deployment!')">Test TAMY</button>
    </div>
    <p>Created by Calvin Nsamba</p>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "TAMY is running", "version": "1.0"}
