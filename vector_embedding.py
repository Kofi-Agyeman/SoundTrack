import json

# Load your enhanced SFX list
with open('sfx_list_enhanced.json', 'r') as f:
    sfx_list = json.load(f)

# Build a list of texts and IDs
texts = []
sound_ids = []

for sound in sfx_list:
    text = f"title: {sound['title']}, description: {sound.get('description', '')}, tags: {sound['tags']}, category: {sound['category']}"
    texts.append(text)
    sound_ids.append(sound['id'])
