from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import re
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper: Convert HEX to RGBA
def hex_to_rgba(hex_color: str):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, 255)
    elif len(hex_color) == 8:
        r, g, b, a = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16)
        return (r, g, b, a)
    else:
        raise ValueError("Invalid HEX format. Use 6 (RGB) or 8 (RGBA) characters.")

@app.get("/")
async def root():
    return {"message": "FastAPI Background Remover is running!"}

@app.post("/remove-bg")
async def remove_background(
    image: UploadFile = File(...),
    hex_color: str = Form(...)
):
    try:
        # Validate hex color
        if not re.fullmatch(r"#[0-9A-Fa-f]{6,8}", hex_color):
            return JSONResponse(
                content={"error": "Invalid HEX format. Use #RRGGBB or #RRGGBBAA."},
                status_code=400
            )

        rgba_color = hex_to_rgba(hex_color)

        # Read and remove background
        input_bytes = await image.read()
        output_bytes = remove(input_bytes)

        # Compose final image with new background
        output_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        width, height = output_img.size
        new_bg = Image.new("RGBA", (width, height), rgba_color)
        new_bg.paste(output_img, (0, 0), mask=output_img.split()[3])

        # Stream image
        buffer = io.BytesIO()
        new_bg.save(buffer, format="PNG")
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png", headers={
            "Content-Disposition": "attachment; filename=processed_image.png"
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Start the server if run directly (for Render)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
