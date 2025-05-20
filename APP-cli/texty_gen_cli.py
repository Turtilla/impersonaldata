#!/usr/bin/env python3

import os
import json
import argparse
import re
import html
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# Configuration paths
CONFIG_PATH = "config.json"
TEXTS_FOLDER = "texts"
TEXTY_FOLDER = "texty"
PNG_FOLDER = os.path.join(TEXTY_FOLDER, "PNG")
MINI_FOLDER = os.path.join(TEXTY_FOLDER, "PNGmini")
SVG_FOLDER = os.path.join(TEXTY_FOLDER, "SVG")

# Ensure output folders exist
for folder in [PNG_FOLDER, MINI_FOLDER, SVG_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate Texty visualizations from a JSON or JSONL file."
    )
    parser.add_argument('--data_file', required=True, help="Input file (JSON or JSONL with objects)")
    parser.add_argument('--Categories_file', required=False, help="JSON config file with categories")
    parser.add_argument('--output_name', required=False, help="Optional base name (overridden in batch mode)")
    return parser.parse_args()

def load_category_colors(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    return {entry["category"]: entry["color"] for entry in config["categories"]}

def segment_to_words(segments):
    words = []
    for segment, color in segments:
        tokens = re.split(r'(\s+)', segment)
        for token in tokens:
            if token.strip():
                words.append((token, color))
    return words

def wrap_words(draw, words, max_width, font):
    lines, line, line_width = [], [], 0
    space_width = draw.textbbox((0, 0), " ", font=font)[2]
    for word, color in words:
        word_width = draw.textbbox((0, 0), word, font=font)[2]
        if line and line_width + space_width + word_width > max_width:
            lines.append(line)
            line, line_width = [(word, color)], word_width
        else:
            line.append((word, color))
            line_width += word_width + (space_width if line else 0)
    if line:
        lines.append(line)
    return lines

def generate_texty_visuals(text_data, output_base, category_colors):
    text = text_data.get("text", "")
    labels = sorted(text_data.get("label", []), key=lambda x: x[0])

    segments = []
    last = 0
    for start, end, cat in labels:
        if last < start:
            segments.append((text[last:start], "#000000"))
        segments.append((text[start:end], category_colors.get(cat, "#000000")))
        last = end
    if last < len(text):
        segments.append((text[last:], "#000000"))

    words = segment_to_words(segments)

    A4_WIDTH = 800
    A4_HEIGHT = int(A4_WIDTH * 1.414)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    dummy_img = Image.new("RGB", (A4_WIDTH, A4_HEIGHT))
    dummy_draw = ImageDraw.Draw(dummy_img)

    best_font_size = 10
    for size in range(10, 300):
        test_font = ImageFont.truetype(font_path, size)
        lines = wrap_words(dummy_draw, words, A4_WIDTH - 20, test_font)
        total_height = len(lines) * (test_font.getbbox("A")[3] + 5)
        if total_height >= A4_HEIGHT - 20:
            break
        best_font_size = size

    font = ImageFont.truetype(font_path, best_font_size)
    img = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    svg_elements = []
    y = 10
    space_width = draw.textbbox((0, 0), " ", font=font)[2]

    for line in wrap_words(draw, words, A4_WIDTH - 20, font):
        x = 10
        for word, color in line:
            w = draw.textbbox((0, 0), word, font=font)[2]
            h = draw.textbbox((0, 0), word, font=font)[3]
            if color != "#000000":
                draw.rectangle([x - 2, y - 5, x + w + 2, y + h + 5], fill=color)
                draw.text((x, y), word, fill=color, font=font)
            else:
                draw.text((x, y), word, fill="white", font=font)
            svg_elements.append({
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "word": word,
                "color": color
            })
            x += w + space_width
        y += font.getbbox("A")[3] + 5

    # Save PNG
    png_path = os.path.join(PNG_FOLDER, f"{output_base}.png")
    img.save(png_path, "PNG")

    # Save mini PNG
    mini_img = img.resize((int(A4_WIDTH * 0.2), int(A4_HEIGHT * 0.2)), Image.LANCZOS)
    mini_path = os.path.join(MINI_FOLDER, f"{output_base}-mini.png")
    mini_img.save(mini_path, "PNG")

    # Save SVG
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4_WIDTH}" height="{A4_HEIGHT}">\n'
    svg += '<rect width="100%" height="100%" fill="white" />\n'
    for el in svg_elements:
        text_y = el["y"] + el["height"]
        if el["color"] != "#000000":
            svg += f'<rect x="{el["x"] - 2}" y="{el["y"] - 5}" width="{el["width"] + 4}" height="{el["height"] + 10}" fill="{el["color"]}" />\n'
            escaped = html.escape(el["word"], quote=True)
            svg += f'<text x="{el["x"]}" y="{text_y}" fill="{el["color"]}" stroke="{el["color"]}" stroke-width="1" font-size="{best_font_size}" font-family="DejaVu Sans">{escaped}</text>\n'


        else:
            svg += f'<text x="{el["x"]}" y="{text_y}" fill="white" stroke="white" stroke-width="1" font-size="{best_font_size}" font-family="DejaVu Sans">{html.escape(el["word"], quote=True)}</text>\n'
    svg += "</svg>"
    svg_path = os.path.join(SVG_FOLDER, f"{output_base}.svg")
    with open(svg_path, "w") as f:
        f.write(svg)

    print(f"[✓] Saved: {png_path}, {mini_path}, {svg_path}")

def load_json_objects(data_file_path):
    return pd.read_json(data_file_path, lines=True)
    with open(data_file_path, "r") as f:
        raw = f.read().strip()
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    # Try JSON lines
    objects = []
    with open(data_file_path, "r") as f:
        for i, line in enumerate(f, start=1):
            try:
                obj = json.loads(line)
                objects.append(obj)
            except json.JSONDecodeError:
                print(f"[!] Skipping invalid JSON object at line {i}")
    return objects

def main():
    args = parse_arguments()

    config_path = args.Categories_file if args.Categories_file else CONFIG_PATH
    if not os.path.isfile(config_path):
        print(f"[!] Configuration file not found: {config_path}")
        exit(1)

    category_colors = load_category_colors(config_path)
    base_filename = os.path.splitext(os.path.basename(args.data_file))[0]

    objects = load_json_objects(args.data_file)
    if objects.empty:
        print("[!] No valid objects found in input.")
        exit(1)

    for obj in objects.iterrows():
        obj_id = obj[1].get("id")
        if not obj_id:
            print("[!] Skipping object without 'id'")
            continue
        output_base = f"{base_filename}-{obj_id}"
        generate_texty_visuals(obj[1], output_base, category_colors)

if __name__ == "__main__":
    main()
