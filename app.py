from flask import Flask, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import os

# Initialize Flask app
app = Flask(__name__)

# Create directories if they don't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('processed', exist_ok=True)

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    if 'image' not in request.files or 'hex_color' not in request.form:
        return jsonify({'error': 'Missing image file or hex_color'}), 400
    
    file = request.files['image']
    hex_color = request.form['hex_color']
    
    try:
        # Load image
        img = Image.open(file).convert("RGBA")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Remove background
        output_bytes = remove(img_bytes.read())
        output_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        
        # Create new background
        width, height = output_img.size
        bg_color = (int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16), 255)
        new_bg = Image.new("RGBA", (width, height), bg_color)
        new_bg.paste(output_img, (0, 0), mask=output_img)
        
        # Save processed image
        output_path = os.path.join('processed', 'output.png')
        new_bg.save(output_path)
        
        return send_file(output_path, mimetype='image/png', as_attachment=True, download_name='processed_image.png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render provides a PORT, default to 5000
    app.run(host='0.0.0.0', port=port)
