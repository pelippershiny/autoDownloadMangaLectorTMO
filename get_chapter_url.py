import cloudscraper
from bs4 import BeautifulSoup
import csv
import re
import os
import sys

# Función para escribir en el archivo log.txt
def log_message(message):
    with open("log.txt", "a") as log_file:
        log_file.write(f"{message}\n")

# Verificar si se pasa la URL como argumento
if len(sys.argv) < 2:
    print("Por favor, proporciona la URL del manga como primer argumento.")
    sys.exit(1)

# Obtener la URL del manga desde el primer argumento
manga_url = sys.argv[1]
log_message(f"Usando la URL del manga: {manga_url}")

# Crear un scraper para evadir Cloudflare
scraper = cloudscraper.create_scraper()

# Hacer una solicitud a la página
try:
    response = scraper.get(manga_url)
    if response.status_code != 200:
        log_message(f"Error al acceder a la URL. Código de estado: {response.status_code}")
        sys.exit(1)
except Exception as e:
    log_message(f"Error al hacer la solicitud: {e}")
    sys.exit(1)

soup = BeautifulSoup(response.content, 'html.parser')

# Obtener y formatear el título
page_title = soup.title.string.strip()
formatted_title = re.sub(r'^\s*(.*?)\s+-\s+Manga\s+-\s*.*$', r'\1', page_title)
log_message(f"Título del manga: {formatted_title}")

# Buscar todas las coincidencias de capítulos usando el path especificado
chapter_elements = soup.select('div#chapters ul.list-group li.list-group-item h4 a.btn-collapse')

# Lista para almacenar los capítulos y sus enlaces
chapters_data = []

# Función para limpiar el texto del capítulo
def format_chapter_text(text):
    # Eliminar comillas dobles y limpiar el texto
    text = text.replace('""', '').strip()
    # Reemplazar múltiples espacios por uno solo
    text = re.sub(r'\s+', ' ', text)
    return text

# Función para ajustar el formato del capítulo
def adjust_chapter_format(text):
    # Buscar el patrón del capítulo y ajustar el formato
    match = re.match(r'(Capítulo \d+\.\d+)\s*(.*)', text)
    if match:
        chapter_num, chapter_title = match.groups()
        return f"{chapter_num}, {chapter_title}"
    return text

# Recorrer los capítulos y buscar el enlace asociado con el capítulo
for chapter in chapter_elements:
    chapter_text = chapter.get_text(strip=True)
    formatted_text = format_chapter_text(chapter_text)
    formatted_text = adjust_chapter_format(formatted_text)
    
    # Encontrar el enlace dentro del mismo "li" que contiene el capítulo
    parent_li = chapter.find_parent('li')
    if parent_li:
        link_element = parent_li.select_one('ul.list-group li.list-group-item div a.btn')
        if link_element and 'href' in link_element.attrs:
            link_url = link_element['href']
            # Asegurarse de que la URL sea completa
            if not link_url.startswith('http'):
                link_url = 'https://visortmo.com' + link_url
            chapters_data.append([formatted_text, link_url])

# Exportar los resultados a un archivo CSV con tres columnas
temp_csv_path = 'temp_result.csv'
with open(temp_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Capítulo', 'Enlace', 'Título'])
    for chapter_text, link_url in chapters_data:
        parts = chapter_text.split(', ', 1)
        if len(parts) == 2:
            csv_writer.writerow([parts[0], link_url, formatted_title])
        else:
            csv_writer.writerow([parts[0], link_url, formatted_title])

log_message(f"Archivo CSV temporal creado: {temp_csv_path}")

# Leer el archivo CSV temporal y escribir el archivo CSV final
final_csv_path = 'result.csv'
with open(temp_csv_path, 'r', encoding='utf-8') as temp_csvfile, \
     open(final_csv_path, 'w', newline='', encoding='utf-8') as final_csvfile:
    csv_reader = csv.reader(temp_csvfile)
    csv_writer = csv.writer(final_csvfile)
    next(csv_reader, None)
    csv_writer.writerow(['Capítulo', 'Enlace', 'Título'])
    for row in csv_reader:
        if len(row) >= 2:
            csv_writer.writerow([row[0], row[1], formatted_title])

# Borrar el archivo CSV temporal
os.remove(temp_csv_path)
log_message(f"Archivo CSV temporal eliminado: {temp_csv_path}")

print("Resultados exportados a 'result.csv'.")
log_message(f"Archivo CSV final creado: {final_csv_path}")
