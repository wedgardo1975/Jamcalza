import boto3
import pandas as pd
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
tabla = dynamodb.Table("INVENTARIO")

df = pd.read_csv("inventario_jamcalza_limpio.csv")

with tabla.batch_writer() as batch:
    for _, fila in df.iterrows():
        batch.put_item(Item={
            "NOMBRE": str(fila["NOMBRE"]).strip(),
            "categoria": str(fila["CATEGORIA"]).strip(),
            "talla": Decimal(str(fila["TALLA"])),
            "stock": Decimal(str(fila["STOCK TOTAL"])),
            "imagen_url": f"https://jamcalza-store-imagenes.s3.amazonaws.com/{str(fila['IMAGEN']).strip()}"
        })

print("Inventario corregido y recargado en DynamoDB.")