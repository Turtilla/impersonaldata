# Texty CLI Image Generator

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This script generates high-quality PNG, mini PNG, and SVG visualizations of text with labeled segments. It's designed to process a file with multiple annotated text entries and create one image per entry, applying category-based coloring.

---

## ✅ Features

- Supports JSON Lines or regular JSON list format as input
- Generates:
  - Full-size PNG images → `texty/PNG/`
  - Mini PNGs (20% scale) → `texty/PNGmini/`
  - SVG vector versions → `texty/SVG/`
- Automatic text wrapping and justified layout
- Detects and escapes special characters for SVG compatibility

---

## 📦 Configuration

The script reads a JSON file (`config.json`) containing category-color mappings like:

```json
{
  "categories": [
    { "category": "name", "color": "#f94144" },
    { "category": "location", "color": "#f3722c" }
  ]
}
```

---

## 🛠️ Usage

```bash
python3 texty_gen_cli.py --data_file mydata.jsonl --Categories_file config.json
```

Optional arguments:
- `--output_name` → Optional name base (only used in single-entry mode)

Each JSON object in the `data_file` should contain:
```json
{
  "id": "001",
  "text": "Hello world...",
  "label": [[0, 5, "name"], [6, 11, "location"]]
}
```

---

## 🖥 Requirements

### For Linux (Debian/Ubuntu)

```bash
sudo apt install python3 python3-pip fonts-dejavu-core
pip3 install pillow
```

### For macOS

```bash
brew install python3
pip3 install pillow
```

Ensure DejaVu Sans font is available (or modify the script to point to another `.ttf` file).

### For Windows

1. Install Python from [https://python.org](https://python.org)
2. Run in Command Prompt or PowerShell:
   ```bash
   pip install pillow
   ```

Make sure DejaVu Sans is installed or adjust the font path in the script.

---

## 📁 Output Folders

Images are saved automatically in:

- `texty/PNG/` → Full resolution PNGs
- `texty/PNGmini/` → Scaled down thumbnails
- `texty/SVG/` → Scalable vector graphics

---

## 📌 Notes

- Words without a label are rendered in white (invisible text)
- Words with a label are displayed with a colored background and stroke
- Only objects with an `"id"` field are processed
