import os

def load_message(name):
    """Зчитує текст повідомлення з resources/messages/"""
    path = os.path.join('resources', 'messages', f"{name}.txt")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_prompt(name):
    """Зчитує промпт для ШІ з resources/prompts/"""
    path = os.path.join('resources', 'prompts', f"{name}.txt")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_image_path(name):
    """Повертає повний шлях до картинки в resources/images/"""
    return os.path.join('resources', 'images', name)