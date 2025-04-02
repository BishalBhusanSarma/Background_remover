from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Background Remover API is running!"

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    if 'image' not in request.files or 'hex_color' not in request.form:
        return jsonify({'error': 'Missing image file or hex_color'}), 400
    
    file = request.files['image']
    hex_color = request.form['hex_color']
    
    try:
        img = Image.open(file).convert("RGBA")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        output_bytes = remove(img_bytes.read())
        output_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        
        width, height = output_img.size
        bg_color = (int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16), 255)
        new_bg = Image.new("RGBA", (width, height), bg_color)
        new_bg.paste(output_img, (0, 0), mask=output_img)
        
        # Serve image directly without saving it
        img_io = io.BytesIO()
        new_bg.save(img_io, format="PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='processed_image.png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port
    app.run(host='0.0.0.0', port=port)
