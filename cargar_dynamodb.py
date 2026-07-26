import boto3
import pandas as pd
from decimal import Decimal, InvalidOperation

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
tabla = dynamodb.Table("INVENTARIO")

# Separador fijo: tu archivo usa punto y coma (;), no coma
df = pd.read_csv("inventario_limpio.csv", sep=";")
df.columns = [c.strip().upper() for c in df.columns]  # normaliza encabezados

nombres_en_csv = set(df["NOMBRE"].astype(str).str.strip())


def limpiar_precio(valor):
    """Convierte cualquier formato de precio (con $, comas, espacios) a Decimal, o None si no es válido."""
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if texto == "" or texto.upper() in ("N/A", "NA", "-"):
        return None
    texto = texto.replace("$", "").replace(" ", "")
    if "," in texto and "." not in texto:
        # Formato tipo 25,99 -> se interpreta como decimal
        texto = texto.replace(",", ".")
    else:
        # Coma como separador de miles, ej. 1,250.00 -> 1250.00
        texto = texto.replace(",", "")
    try:
        return Decimal(texto)
    except InvalidOperation:
        print(f"⚠ Precio inválido, se omite: '{valor}'")
        return None


# 1. Agregar y/o actualizar todos los productos que están en el CSV
with tabla.batch_writer() as batch:
    for _, fila in df.iterrows():
        nombre = str(fila["NOMBRE"]).strip()
        # La imagen siempre se llama igual que el producto + .jpg (así las nombra optimizar.py)
        imagen = f"{nombre}.jpg"

        item = {
            "NOMBRE": nombre,
            "categoria": str(fila["CATEGORIA"]).strip(),
            "talla": Decimal(str(fila["TALLA"])),
            "stock": Decimal(str(fila["STOCK TOTAL"])),
            "imagen_url": f"https://jamcalza-store-imagenes.s3.amazonaws.com/{imagen}"
        }

        if "PRECIO" in df.columns:
            precio_limpio = limpiar_precio(fila["PRECIO"])
            if precio_limpio is not None:
                item["precio"] = precio_limpio

        if "UBICACION" in df.columns and pd.notna(fila["UBICACION"]):
            item["ubicacion"] = str(fila["UBICACION"]).strip()

        batch.put_item(Item=item)

print(f"✔ {len(df)} productos agregados/actualizados en DynamoDB.")

# 2. Eliminar de DynamoDB los productos que YA NO están en el CSV
respuesta = tabla.scan()
productos_actuales = respuesta.get("Items", [])

eliminados = 0
with tabla.batch_writer() as batch:
    for producto in productos_actuales:
        if producto["NOMBRE"] not in nombres_en_csv:
            batch.delete_item(Key={"NOMBRE": producto["NOMBRE"]})
            print(f"🗑 Eliminado de DynamoDB: {producto['NOMBRE']}")
            eliminados += 1

print(f"✔ {eliminados} producto(s) eliminados por no estar en el CSV.")
print("Inventario sincronizado por completo.")