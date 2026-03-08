import os

def load_message(name):
    path = os.path.join('resources', 'messages', f"{name}.txt")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_prompt(name):
    path = os.path.join('resources', 'prompts', f"{name}.txt")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_image_path(name):
    return os.path.join('resources', 'images', name)