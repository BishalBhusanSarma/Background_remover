from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from rembg import remove
from PIL import Image
import io
import os

app = FastAPI()

os.makedirs("processed", exist_ok=True)  # Ensure directory exists

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}

@app.post("/remove-bg")
async def remove_background(image: UploadFile = File(...), hex_color: str = Form(...)):
    try:
        img = Image.open(image.file).convert("RGBA")
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        # Remove background
        output_bytes = remove(img_bytes.read())
        output_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        
        # Replace background color
        width, height = output_img.size
        bg_color = (int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16), 255)
        new_bg = Image.new("RGBA", (width, height), bg_color)
        new_bg.paste(output_img, (0, 0), mask=output_img)
        
        output_path = "processed/output.png"
        new_bg.save(output_path)

        return FileResponse(output_path, media_type="image/png", filename="processed_image.png")
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log error
        return JSONResponse(content={"error": str(e)}, status_code=500)
