import os
import json
import time
import requests

# === CONFIG ===
HF_API_TOKEN = "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"  
MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"  # or another model you want to use

INPUT_FILE = "sfx_list.json"
OUTPUT_FILE = "sfx_list_enhanced.json"

# Rate limiting (be gentle with free API)
DELAY_BETWEEN_REQUESTS = 2.0  # seconds

def generate_description_hf(title, tags, category):
    """Use Hugging Face Router API to generate a detailed SFX description."""
    prompt = f"""You are a professional sound designer. Write a short, vivid description (1–2 sentences) for a sound effect, suitable for an SFX library.

Sound:
- Title: {title}
- Tags: {tags}
- Category: {category}

Description (focus on how it sounds, texture, pitch, intensity, and context):"""

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional sound designer. Write short, vivid descriptions for sound effects."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return f"Generated description for {title} (AI failed)"
        else:
            print(f"HF Router error {response.status_code}: {response.text}")
            return f"Generated description for {title} (AI failed)"
    except Exception as e:
        print(f"Error calling Hugging Face Router: {e}")
        return f"Generated description for {title} (AI failed)"

def enhance_sfx_descriptions(input_file, output_file):
    """Load sfx_list.json, generate detailed descriptions, and save enhanced version."""
    with open(input_file, 'r', encoding='utf-8') as f:
        sfx_list = json.load(f)
    
    print(f"Loaded {len(sfx_list)} sounds. Enhancing descriptions with Hugging Face Router...")

    enhanced_list = []
    for sound in sfx_list:
        current_desc = sound.get("description", "").strip()
        if len(current_desc) < 20 or "sound effect" in current_desc.lower():
            print(f"Enhancing: {sound['title']} ({sound['category']})")
            new_desc = generate_description_hf(
                title=sound["title"],
                tags=sound["tags"],
                category=sound["category"]
            )
            sound["description"] = new_desc
        
        enhanced_list.append(sound)
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_list, f, indent=2, ensure_ascii=False)
    
    print(f"Enhanced metadata saved to {output_file}")

# === RUN ===
if __name__ == "__main__":
    enhance_sfx_descriptions(INPUT_FILE, OUTPUT_FILE)
