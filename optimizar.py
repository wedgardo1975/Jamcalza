import os
from PIL import Image

# Configura tus carpetas aquí (puedes cambiar los nombres si lo deseas)
carpeta_origen = "imagenes_originales"
carpeta_destino = "imagenes_optimizadas"

# Crear las carpetas automáticamente si no existen
if not os.path.exists(carpeta_origen):
    os.makedirs(carpeta_origen)
if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

print(f"Coloca tus fotos dentro de la carpeta: {os.path.abspath(carpeta_origen)}")

# Procesar cada archivo
archivos = os.listdir(carpeta_origen)
contador = 0

for archivo in archivos:
    if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            ruta_origen = os.path.join(carpeta_origen, archivo)
            ruta_destino = os.path.join(carpeta_destino, archivo.split('.')[0] + ".jpg")
            
            # Abrir y procesar la imagen
            img = Image.open(ruta_origen)
            img.thumbnail((1200, 1200))
            
            # Convertir a RGB si es necesario (evita errores con PNGs transparentes)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Guardar con compresión optimizada
            img.save(ruta_destino, "JPEG", quality=78, optimize=True)
            print(f"✔ Optimizada: {archivo}")
            contador += 1
        except Exception as e:
            print(f"❌ Error con {archivo}: {e}")

print(f"\n¡Proceso terminado! Imágenes optimizadas con éxito: {contador}")
