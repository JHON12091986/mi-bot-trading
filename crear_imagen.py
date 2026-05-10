from PIL import Image, ImageDraw, ImageFont

def crear_imagen_con_texto(guion, imagen_fondo, nombre_salida):
    with Image.open(imagen_fondo) as img:
        img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 50)
        except:
            font = ImageFont.load_default()
        
        lineas = guion.split('\n')
        y = 900
        for linea in lineas:
            draw.text((540, y), linea, fill=(255, 255, 0), font=font, anchor="mm")
            y += 60
        
        img.save(nombre_salida)
        print(f"✅ Imagen creada: {nombre_salida}")

if __name__ == "__main__":
    guion = "⚠️ SEÑAL DE VENTA - MU\nRSI: 87.8\nPrecio: $481.72"
    imagen_fondo = r"C:\Users\jhons\mi_primer_bot\fondo.jpg"
    crear_imagen_con_texto(guion, imagen_fondo, "imagen_con_texto.jpg")