import os
from PIL import Image, ImageDraw, ImageFont

def crear_icono(size, filename):
    # Crear una imagen con canal alfa (RGBA)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dibujar círculo de fondo Azul Rey Oscuro (#1E3A8A)
    margin = int(size * 0.05)
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=(30, 58, 138, 255) # #1E3A8A
    )
    
    # Dibujar un borde elegante en Cyan (#0EA5E9)
    border_width = max(2, int(size * 0.03))
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        outline=(14, 165, 233, 255),
        width=border_width
    )
    
    # Intentar cargar una fuente predeterminada o del sistema
    try:
        # Intentar cargar Arial Bold del sistema Windows
        font_path = "C:\\Windows\\Fonts\\arialbd.ttf"
        if not os.path.exists(font_path):
            font_path = "arial.ttf"
        font_size = int(size * 0.45)
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        # Fallback a fuente básica por defecto si falla truetype
        font = ImageFont.load_default()

    # Escribir la letra "S" en el centro en color blanco
    texto = "S"
    
    # Medir texto
    if hasattr(font, "getbbox"):
        # Pillow >= 9.2.0
        bbox = draw.textbbox((0, 0), texto, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    else:
        text_w, text_h = draw.textsize(texto, font=font)
        
    # Calcular posición centrada
    x = (size - text_w) / 2
    # Ajuste manual vertical para fuentes truetype para que se vea perfectamente centrado
    y = (size - text_h) / 2.3
    
    draw.text((x, y), texto, fill=(255, 255, 255, 255), font=font)
    
    # Guardar
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, "PNG")
    print(f"Icono creado: {filename} ({size}x{size})")

if __name__ == "__main__":
    public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
    crear_icono(192, os.path.join(public_dir, "pwa-192x192.png"))
    crear_icono(512, os.path.join(public_dir, "pwa-512x512.png"))
