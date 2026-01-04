import os
import json
from pathlib import Path
# Use wave/mutagen instead of TinyTag to read audio metadata (no external TinyTag dependency)
def generate_tags_from_filename(filename):
    """Generate simple tags from filename (remove extension, split by _/-/spaces)."""
    name = Path(filename).stem.lower()
    # Replace separators with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    # Split into words and remove common noise
    words = [w for w in name.split() if w not in {'01', '02', '03', '04', '05', '06', '07', '08', '09', '10', 'short', 'long', 'loop', 'v1', 'v2'}]
    return ', '.join(words)

def get_category_from_path(path, base_dir):
    """Guess category from folder name (e.g., /sounds/ui/ → 'ui')."""
    rel_path = Path(path).relative_to(base_dir)
    if len(rel_path.parts) >= 1:
        folder = rel_path.parts[0].lower()
        if folder in ['ui', 'interface', 'gui']:
            return 'ui'
        elif folder in ['explosion', 'explosions', 'boom', 'blast']:
            return 'explosion'
        elif folder in ['nature', 'ambience', 'ambience', 'environment']:
            return 'nature'
        elif folder in ['weapon', 'weapons', 'gun', 'laser']:
            return 'weapon'
        elif folder in ['character', 'voice', 'dialogue']:
            return 'character'
        elif folder in ['music', 'bgm', 'background']:
            return 'music'
        else:
            return folder
    return 'misc'

def extract_metadata_for_sfx(sounds_dir):
    """Scan sounds_dir and return a list of SFX metadata."""
    sounds_dir = Path(sounds_dir)
    sfx_list = []
    id_counter = 1

    for file_path in sounds_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ['.wav', '.mp3', '.ogg', '.flac', '.aiff', '.aif']:
            try:
                # Read audio metadata (use wave for WAV, mutagen for other formats if available)
                duration = 0.0
                sample_rate = 44100
                channels = 1
                ext = file_path.suffix.lower()
                if ext == '.wav':
                    try:
                        import wave
                        with wave.open(str(file_path), 'rb') as wf:
                            frames = wf.getnframes()
                            sample_rate = wf.getframerate() or sample_rate
                            channels = wf.getnchannels() or channels
                            duration = frames / float(sample_rate) if sample_rate else 0.0
                    except Exception:
                        # Could not read WAV with wave module; keep defaults
                        pass
                else:
                    try:
                        import importlib
                        mutagen_mod = importlib.import_module('mutagen')
                        MutagenFile = getattr(mutagen_mod, 'File', None)
                        if MutagenFile is not None:
                            m = MutagenFile(str(file_path))
                            if m is not None and hasattr(m, 'info'):
                                info = m.info
                                duration = getattr(info, 'length', duration) or duration
                                sample_rate = getattr(info, 'sample_rate', sample_rate) or sample_rate
                                channels = getattr(info, 'channels', channels) or channels
                    except Exception:
                        # mutagen not available or failed, keep defaults
                        pass

                # Generate fields
                filename = file_path.name
                path = str(file_path.resolve()).split("static\\")[1]
                size_bytes = file_path.stat().st_size

                # Use filename as title (without extension)
                title = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()

                # Generate tags from filename
                tags = generate_tags_from_filename(filename)

                # Guess category from folder
                category = get_category_from_path(file_path, sounds_dir)

                # Optional: add a simple description
                description = f"{title} sound effect"

                # Add to list
                sfx_list.append({
                    "id": id_counter,
                    "filename": filename,
                    "path": path,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "category": category,
                    "duration": round(duration, 3),
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "size_bytes": size_bytes,
                    "source": "my-library",  # or extract from folder if needed
                    "license": "personal"   # change as needed
                })
                id_counter += 1

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return sfx_list

# === CONFIG ===
SOUNDS_DIR ="C:\\Users\\P A V I L I O N\\Documents\\VS studio\\SoundTrack\\static\\Resources" # ← CHANGE THIS to your sounds folder
OUTPUT_FILE = "sfx_list.json"

# === RUN ===
if __name__ == "__main__":
    print(f"Scanning {SOUNDS_DIR}...")
    sfx_data = extract_metadata_for_sfx(SOUNDS_DIR)
    print(f"Found {len(sfx_data)} sounds.")

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sfx_data, f, indent=2, ensure_ascii=False)

    print(f"Metadata saved to {OUTPUT_FILE}")
