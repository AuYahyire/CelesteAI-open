import base64
import httpx
import io
from PIL import Image
from bot.core.logger import get_logger

logger = get_logger("image_utils")

async def file_id_to_resized_base64(file_path: str, size=(512, 512)) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(file_path)
        resp.raise_for_status()
        img_bytes = io.BytesIO(resp.content)

    try:
        with Image.open(img_bytes) as img:
            img = img.convert('RGB')
            img = img.resize(size, Image.LANCZOS)
            out_bytes = io.BytesIO()
            img.save(out_bytes, format="JPEG")
            out_bytes.seek(0)
            b64 = base64.b64encode(out_bytes.read()).decode('utf-8')
            return b64
    except Exception:
        return None

async def extraer_imagenes_base64(mensaje, contexto, size=(512,512)):
    base64_imgs = []
    if not mensaje:
        return base64_imgs

    if mensaje.photo:
        try:
            file = await contexto.bot.get_file(mensaje.photo[-1].file_id)
            base64_str = await file_id_to_resized_base64(file.file_path, size)
            if base64_str:
                base64_imgs.append(base64_str)
        except Exception as e:
            logger.info(f"Error al extraer imagen: {e}")
    
    if mensaje.sticker:
        try:
            file = await contexto.bot.get_file(mensaje.sticker.file_id)
            base64_str = await file_id_to_resized_base64(file.file_path, size)
            if base64_str:
                base64_imgs.append(base64_str)
        except Exception:
            pass

    return base64_imgs