import os
import cloudscraper
import shutil
from bs4 import BeautifulSoup
from PIL import Image
import sys
import time
import logging

# Configurar el logging para que escriba en log.txt
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_url(url):
    # Verificar si la URL termina en '/paginated' y modificarla a '/cascade'
    if url.endswith('/paginated'):
        url = url[:-10] + '/cascade'
    logging.info(f"URL procesada: {url}")
    return url

def download_images(title, chapter, url):
    # Crear la carpeta con formato {title} - {chapter}
    output_folder = f'{title} - {chapter}'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info(f"Carpeta creada: {output_folder}")

    # Usar cloudscraper para evadir Cloudflare y agregar headers de un navegador real
    scraper = cloudscraper.create_scraper()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0",
        "Referer": url,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "es-ES,es;q=0.9",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Opera GX";v="112"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }

    # Obtener el contenido HTML de la página
    logging.info(f"Accediendo a la URL: {url}")
    response = scraper.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Esperar 5 segundos para que las imágenes se carguen después de la petición
    logging.info("Esperando 5 segundos para que las imágenes se carguen completamente...")
    time.sleep(5)

    # Encontrar todas las imágenes en la página
    images = soup.find_all('img')

    # Descargar y guardar las imágenes en la carpeta
    for idx, img in enumerate(images):
        # Obtener la URL de la imagen
        img_url = img.get('src')
        if img.get('data-src'):
            img_url = img['data-src']

        # Asegurarse de que la URL de la imagen sea completa
        if not img_url.startswith('http'):
            img_url = 'https://visortmo.com' + img_url

        # Mostrar la URL de la imagen que se intenta descargar
        logging.info(f"Intentando descargar la imagen {idx + 1} de la URL: {img_url}")
        
        # Descargar la imagen
        img_response = scraper.get(img_url, headers=headers, stream=True)

        # Guardar la imagen temporalmente como .webp
        image_path_webp = os.path.join(output_folder, f'{idx + 1}.webp')
        with open(image_path_webp, 'wb') as out_file:
            shutil.copyfileobj(img_response.raw, out_file)

        # Convertir la imagen a .png
        image_path_png = os.path.join(output_folder, f'{idx + 1}.png')
        try:
            img_webp = Image.open(image_path_webp).convert("RGB")
            img_webp.save(image_path_png, 'PNG')
            logging.info(f"Imagen {idx + 1} descargada y convertida a PNG: {image_path_png}")
        except Exception as e:
            logging.error(f"Error al convertir la imagen {idx + 1}: {e}")

        # Eliminar la imagen temporal .webp
        os.remove(image_path_webp)

    logging.info(f"Descarga y conversión completada. Las imágenes se guardaron en la carpeta '{output_folder}'.")

    # Comprimir la carpeta después de la descarga
    zip_output = shutil.make_archive(output_folder, 'zip', output_folder)
    logging.info(f"Carpeta comprimida: {zip_output}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        logging.error("Uso incorrecto del script. Se requieren 3 argumentos: <titulo> <capitulo> <url>")
        print("Uso: python download_images.py <titulo> <capitulo> <url>")
        sys.exit(1)
    
    # Obtener los argumentos
    title = sys.argv[1]
    chapter = sys.argv[2]
    input_url = sys.argv[3]

    logging.info(f"Argumentos recibidos: Título={title}, Capítulo={chapter}, URL={input_url}")
    
    # Procesar la URL para verificar y modificar el final
    processed_url = process_url(input_url)
    
    # Descargar imágenes desde la URL procesada
    download_images(title, chapter, processed_url)
