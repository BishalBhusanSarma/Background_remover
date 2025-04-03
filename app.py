from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import os

app = FastAPI()

# ✅ Enable CORS (Allow frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this for security)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Ensure directories exist
os.makedirs('processed', exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Background Remover API is running!"}

@app.post("/remove-bg/")
async def remove_background(image: UploadFile = File(...), hex_color: str = Form("#ffffff")):
    try:
        img = Image.open(image.file).convert("RGBA")

        # ✅ Remove background
        output_bytes = remove(io.BytesIO(img.tobytes()).getvalue())
        output_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

        # ✅ Apply new background color
        width, height = output_img.size
        bg_color = (
            int(hex_color[1:3], 16),
            int(hex_color[3:5], 16),
            int(hex_color[5:7], 16),
            255
        )
        new_bg = Image.new("RGBA", (width, height), bg_color)
        new_bg.paste(output_img, (0, 0), mask=output_img)

        # ✅ Save processed image
        output_path = "processed/output.png"
        new_bg.save(output_path)

        return FileResponse(output_path, media_type="image/png", filename="processed_image.png")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
