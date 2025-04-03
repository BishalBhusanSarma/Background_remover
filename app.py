from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import os
import re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this if Live Server runs on a different port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs("processed", exist_ok=True)  # Ensure folder exists

def hex_to_rgba(hex_color: str):
    """Convert HEX to RGBA."""
    hex_color = hex_color.strip().lstrip("#")  # Remove '#' if present
    if len(hex_color) == 6:  # No alpha value provided, assume full opacity (255)
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, 255)
    elif len(hex_color) == 8:  # If 8 characters, includes alpha
        r, g, b, a = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16)
        return (r, g, b, a)
    else:
        raise ValueError("Invalid HEX format. Use 6 (RGB) or 8 (RGBA) characters.")

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}

@app.post("/remove-bg")
async def remove_background(
    image: UploadFile = File(...), 
    hex_color: str = Form(...)
):
    try:
        # Validate HEX color input
        if not re.fullmatch(r"#[0-9A-Fa-f]{6,8}", hex_color):
            return JSONResponse(content={"error": "Invalid HEX format. Use #RRGGBB or #RRGGBBAA."}, status_code=400)

        rgba_color = hex_to_rgba(hex_color)  # Convert HEX to RGBA

        # Open image
        img = Image.open(image.file).convert("RGBA")
        
        # Remove background
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        output_bytes = remove(img_bytes.read())
        output_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

        # Create new background
        width, height = output_img.size
        new_bg = Image.new("RGBA", (width, height), rgba_color)

        # Apply new background
        new_bg.paste(output_img, (0, 0), mask=output_img.split()[3])

        # Save output image
        output_path = "processed/output.png"
        new_bg.save(output_path, format="PNG")

        return FileResponse(output_path, media_type="image/png", filename="processed_image.png")

    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
