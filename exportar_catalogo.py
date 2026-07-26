import json
import boto3
from decimal import Decimal

# Inicializar los recursos de AWS
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
s3 = boto3.client("s3", region_name="us-east-1")

# Nombre exacto de tu tabla real en AWS
tabla = dynamodb.Table("INVENTARIO")

# Función auxiliar para convertir números de DynamoDB a texto/número legible en JSON
def default_convertir(obj):
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    raise TypeError

try:
    print("Buscando productos en DynamoDB...")
    # Escanear los datos de la tabla
    response = tabla.scan()
    productos = response.get("Items", [])
    
    # Convertir los datos a formato JSON limpio
    cuerpo = json.dumps(productos, default=default_convertir, ensure_ascii=False, indent=2)
    
    print(f"Subiendo {len(productos)} productos al bucket de S3...")
    # Subir el archivo JSON directamente a tu bucket de imágenes
    s3.put_object(
        Bucket="jamcalza-store-imagenes", 
        Key="data/catalog.json", 
        Body=cuerpo, 
        ContentType="application/json"
    )
    
    print(f"✔ ¡Éxito! {len(productos)} productos exportados correctamente a data/catalog.json en tu S3.")

except Exception as e:
    print(f"❌ Ocurrió un error durante la exportación: {e}")