import json
import os

def load_resource(file_name):
    # Validar que el nombre del archivo no contenga caracteres peligrosos
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise ValueError("Nombre de archivo no válido")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    resources_path = os.path.join(base_path, "resources")
    file_path = os.path.join(resources_path, file_name)
    
    # Verificar que el archivo esté dentro del directorio resources
    if not file_path.startswith(resources_path):
        raise ValueError("Acceso denegado: archivo fuera del directorio permitido")
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No existe el archivo: {file_name}")
    
    ext = os.path.splitext(file_path)[1].lower()
    with open(file_path, "r", encoding="utf-8") as f:
        if ext == ".txt":
            return f.read()
        if ext == ".json":
            return json.load(f)
    raise ValueError(f"Formato no soportado: {ext}")

def build_input_block(text, images=None):
    if not images:
        return [{"role": "user", "content": text.strip()}]

    content = [{"type": "input_text", "text": text.strip()}]
    for b64 in images:
        content.append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{b64}"
        })
    return [{"role": "user", "content": content}]