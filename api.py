from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid # For generating unique filenames
from emby_gen import generate_emby_cover

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create uploads directory if it doesn't exist

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        # Generate a unique filename to avoid collisions
        unique_filename = str(uuid.uuid4()) + '_' + filename
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        return jsonify({'filepath': filepath}), 200

@app.route('/generate_cover', methods=['POST'])
def generate_cover():
    data = request.json

    # Extract all parameters from the request data
    library_name = data.get('libraryName')
    sub_title = data.get('subTitle')
    posters = data.get('posters', [])
    backdrop_url = data.get('backdropUrl')
    theme = data.get('theme')
    layout_mode = data.get('layoutMode')
    current_font = data.get('currentFont')
    active_text_color = data.get('activeTextColor')
    title_x = data.get('titleX')
    title_y = data.get('titleY')
    title_gap = data.get('titleGap')
    title_size = data.get('titleSize')
    grid_intensity = data.get('gridIntensity')
    poster_x = data.get('posterX')
    fan_spread = data.get('fanSpread')
    fan_rotation = data.get('fanRotation')
    cycle_index = data.get('cycleIndex')

    try:
        output_path = generate_emby_cover(
            library_name=library_name,
            sub_title=sub_title,
            posters=posters,
            backdrop_url=backdrop_url,
            theme=theme,
            layout_mode=layout_mode,
            current_font=current_font,
            active_text_color=active_text_color,
            title_x=title_x,
            title_y=title_y,
            title_gap=title_gap,
            title_size=title_size,
            grid_intensity=grid_intensity,
            poster_x=poster_x,
            fan_spread=fan_spread,
            fan_rotation=fan_rotation,
            cycle_index=cycle_index
        )
        return send_file(output_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)