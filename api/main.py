import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so your video web players can access the stream without restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/main")
def convert_playlist(url: str = Query(..., description="The direct broken .m3u8 URL")):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch source playlist")
            
        # Parse out the base domain dynamically
        parsed_url = url.split('/')
        base_domain = f"{parsed_url[0]}//{parsed_url[2]}"
        
        # Rewrite relative root paths with the full server domain
        lines = response.text.splitlines()
        fixed_lines = []
        
        for line in lines:
            if line.startswith("/"):
                fixed_lines.append(f"{base_domain}{line}")
            else:
                fixed_lines.append(line)
                
        fixed_m3u8 = "\n".join(fixed_lines)
        return PlainTextResponse(content=fixed_m3u8, media_type="application/x-mpegURL")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
