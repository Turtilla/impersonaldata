import os
import json
import re
from flask import Flask, jsonify, request, abort, render_template, send_from_directory
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Route to frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/texty/<path:filename>')
def serve_texty(filename):
    directory = os.path.join(app.root_path, 'texty')
    return send_from_directory(directory, filename)

# Define paths
CONFIG_PATH = "config.json"
TEXTS_FOLDER = "texts"
TEXTY_FOLDER = "texty"
os.makedirs(TEXTY_FOLDER, exist_ok=True)

# Load configuration and create lookup for category colors
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
categories_colors = {cat["category"]: cat["color"] for cat in config["categories"]}

# -----------------------------
# Helper functions for wrapping and justification
# -----------------------------
def segment_to_words(segments):
    """Convert segments (text, color) into a list of (word, color) tuples."""
    words = []
    for segment, color in segments:
        tokens = re.split(r'(\s+)', segment)
        for token in tokens:
            if token.strip() == "":
                continue
            words.append((token, color))
    return words

def wrap_words(draw, words, max_width, font):
    """Wrap words into lines that do not exceed max_width."""
    lines = []
    current_line = []
    current_width = 0
    space_bbox = draw.textbbox((0, 0), " ", font=font)
    space_width = space_bbox[2] - space_bbox[0]
    for word, color in words:
        word_bbox = draw.textbbox((0, 0), word, font=font)
        word_width = word_bbox[2] - word_bbox[0]
        if current_line:
            if current_width + space_width + word_width <= max_width:
                current_line.append((word, color))
                current_width += space_width + word_width
            else:
                lines.append(current_line)
                current_line = [(word, color)]
                current_width = word_width
        else:
            current_line.append((word, color))
            current_width = word_width
    if current_line:
        lines.append(current_line)
    return lines

def justify_line_positions(draw, line, x, y, max_width, font):
    """
    Given a line (list of (word, color)), compute the x positions for each word
    so that the line is justified. Returns a list of dictionaries with word info.
    """
    word_widths = []
    for word, _ in line:
        bbox = draw.textbbox((0, 0), word, font=font)
        word_widths.append(bbox[2] - bbox[0])
    total_words_width = sum(word_widths)
    space_bbox = draw.textbbox((0, 0), " ", font=font)
    space_width = space_bbox[2] - space_bbox[0]
    num_spaces = len(line) - 1
    if num_spaces > 0:
        extra_space = max_width - total_words_width - (num_spaces * space_width)
        added_space = extra_space / num_spaces if extra_space > 0 else 0
    else:
        added_space = 0
    positions = []
    cur_x = x
    for (word, color), w in zip(line, word_widths):
        positions.append({
            "x": cur_x,
            "y": y,
            "word": word,
            "color": color,
            "width": w,
            "height": (draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1])
        })
        cur_x += w + space_width + added_space
    return positions

# -----------------------------
# /api/texty_gen Endpoint
# -----------------------------
@app.route("/api/texty_gen", methods=["POST"])
def texty_gen():
    data = request.get_json()
    if not data or "filename" not in data:
        abort(400, description="Filename is required in the payload.")
    
    filename = data["filename"]
    text_path = os.path.join(TEXTS_FOLDER, filename)
    if not os.path.exists(text_path):
        abort(404, description="File not found.")
    
    with open(text_path, "r") as f:
        text_data = json.load(f)
    
    text_content = text_data.get("text", "")
    labels = text_data.get("label", [])
    labels = sorted(labels, key=lambda x: x[0])
    
    segments = []
    last_idx = 0
    for label in labels:
        start, end, cat = label
        if last_idx < start:
            segments.append((text_content[last_idx:start], "#000000"))  # Un-categorized
        color = categories_colors.get(cat, "#000000")
        segments.append((text_content[start:end], color))
        last_idx = end
    if last_idx < len(text_content):
        segments.append((text_content[last_idx:], "#000000"))
    
    words = segment_to_words(segments)
    
    # A4 dimensions (portrait)
    A4_width = 800
    A4_height = int(A4_width * 1.414)  # ~1131 pixels
    
    dummy_img = Image.new("RGB", (A4_width, A4_height))
    dummy_draw = ImageDraw.Draw(dummy_img)
    
    # Use a TTF font (adjust font_path as needed)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    best_font_size = None
    for size in range(10, 300):
        candidate_font = ImageFont.truetype(font_path, size)
        candidate_lines = wrap_words(dummy_draw, words, max_width=A4_width - 20, font=candidate_font)
        candidate_line_bbox = dummy_draw.textbbox((0, 0), "A", font=candidate_font)
        candidate_line_height = (candidate_line_bbox[3] - candidate_line_bbox[1]) + 5
        candidate_total_height = len(candidate_lines) * candidate_line_height + 20
        if candidate_total_height > A4_height - 20:
            break
        best_font_size = size
    if best_font_size is None:
        best_font_size = 10
    font = ImageFont.truetype(font_path, best_font_size)
    
    # Create main PNG with white background
    img = Image.new("RGB", (A4_width, A4_height), color="white")
    draw = ImageDraw.Draw(img)
    
    lines = wrap_words(draw, words, max_width=A4_width - 20, font=font)
    line_bbox = draw.textbbox((0, 0), "A", font=font)
    line_height = (line_bbox[3] - line_bbox[1]) + 5
    
    svg_elements = []
    y_pos = 10
    space_bbox = draw.textbbox((0, 0), " ", font=font)
    space_width = space_bbox[2] - space_bbox[0]
    
    # Process each line: justify (if not last) or left-align (last)
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            positions = justify_line_positions(draw, line, 10, y_pos, max_width=A4_width - 20, font=font)
        else:
            positions = []
            cur_x = 10
            for word, color in line:
                bbox = draw.textbbox((0, 0), word, font=font)
                w = bbox[2] - bbox[0]
                positions.append({
                    "x": cur_x,
                    "y": y_pos,
                    "word": word,
                    "color": color,
                    "width": w,
                    "height": (draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1])
                })
                cur_x += w + space_width
        # Draw each word and record position info for SVG
        for pos in positions:
            x = pos["x"]
            y = pos["y"]
            word = pos["word"]
            color = pos["color"]
            w = pos["width"]
            if color == "#000000":
                # Un-categorized: draw invisible (white fill and stroke)
                draw.text((x, y), word, fill="white", font=font, stroke_width=1, stroke_fill="white")
            else:
                # Categorized: use padding_x=2, padding_y=5
                padding_x = 2
                padding_y = 5
                bbox = draw.textbbox((x, y), word, font=font)
                h = bbox[3] - bbox[1]
                draw.rectangle([x - padding_x, y - padding_y, x + w + padding_x, y + h + padding_y], fill=color)
                draw.text((x, y), word, fill=color, font=font, stroke_width=1, stroke_fill=color)
            svg_elements.append(pos)
        y_pos += line_height
    
    # Save main PNG image
    png_filename = os.path.splitext(filename)[0] + ".png"
    png_path = os.path.join(TEXTY_FOLDER, png_filename)
    img.save(png_path, "PNG")
    
    # Create mini PNG (20% size) and save with suffix "-mini.png"
    mini_width = int(A4_width * 0.2)
    mini_height = int(A4_height * 0.2)
    mini_img = img.resize((mini_width, mini_height), resample=Image.LANCZOS)
    mini_png_filename = os.path.splitext(filename)[0] + "-mini.png"
    mini_png_path = os.path.join(TEXTY_FOLDER, mini_png_filename)
    mini_img.save(mini_png_path, "PNG")
    
    # Generate SVG output using computed positions
    svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4_width}" height="{A4_height}">'
    svg_header += '<rect width="100%" height="100%" fill="white" />'
    svg_body = ""
    for el in svg_elements:
        x = el["x"]
        y = el["y"]
        word = el["word"]
        w = el["width"]
        h = el["height"]
        color = el["color"]
        text_y = y + h  # adjust for baseline
        if color == "#000000":
            svg_body += (
                f'<text x="{x}" y="{text_y}" fill="white" stroke="white" stroke-width="1" '
                f'font-size="{best_font_size}" font-family="DejaVu Sans">{word}</text>'
            )
        else:
            padding_x = 2
            padding_y = 5
            svg_body += f'<rect x="{x - padding_x}" y="{y - padding_y}" width="{w + 2*padding_x}" height="{h + 2*padding_y}" fill="{color}" />'
            svg_body += (
                f'<text x="{x}" y="{text_y}" fill="{color}" stroke="{color}" stroke-width="1" '
                f'font-size="{best_font_size}" font-family="DejaVu Sans">{word}</text>'
            )
    svg_footer = '</svg>'
    svg_content = svg_header + svg_body + svg_footer
    svg_filename = os.path.splitext(filename)[0] + ".svg"
    svg_path = os.path.join(TEXTY_FOLDER, svg_filename)
    with open(svg_path, "w") as f:
        f.write(svg_content)
    
    return jsonify({
        "message": "Texty image generated successfully.",
        "png_file": png_filename,
        "mini_png_file": mini_png_filename,
        "svg_file": svg_filename,
        "font_size": best_font_size
    })


@app.route("/api/show_texts", methods=["GET"])
def show_texts():
    texts = []
    # List each .json file in the /texts folder
    for filename in os.listdir(TEXTS_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(TEXTS_FOLDER, filename)
            with open(file_path, "r") as f:
                text_data = json.load(f)
                # Optionally, include the filename in the returned data
                text_data["filename"] = filename
                texts.append(text_data)
    return jsonify(texts)



@app.route('/api/textys', methods=['GET'])
def list_textys():
    # Define the path to the texty folder (adjust as needed)
    texty_dir = os.path.join(app.root_path, 'texty')
    
    # If the folder doesn't exist, return an empty list
    if not os.path.exists(texty_dir):
        return jsonify([])
    
    # List all files in the folder (you can filter by extension if needed)
    texty_files = [f for f in os.listdir(texty_dir) if os.path.isfile(os.path.join(texty_dir, f))]
    
    # Return the list of texty files
    return jsonify(texty_files)


if __name__ == "__main__":
    app.run(debug=True)

