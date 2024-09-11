import requests
from bs4 import BeautifulSoup
import subprocess
import sys
import logging

# Configurar el logging para que escriba en log.txt y también muestre en consola
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración del FileHandler para escribir en log.txt
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Configuración del StreamHandler para mostrar en consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

def clear_log_file():
    # Limpiar el contenido del archivo de log al iniciar
    open('log.txt', 'w').close()

def get_search_results(manga_name):
    search_url = f"https://visortmo.com/library?_pg=1&title={manga_name.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0",
    }
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Error al acceder a la página de búsqueda. Código de estado: {response.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer URLs usando el XPath proporcionado
    manga_links = soup.select('#app main .row .col-12.col-lg-8.col-xl-9 .element a')
    results = [(i + 1, link['href'].strip()) for i, link in enumerate(manga_links[:10])]

    return results

def run_script(script_name, *args):
    # Ejecutar un script Python y capturar su salida
    logger.info(f"Ejecutando {script_name} con argumentos: {args}")
    result = subprocess.run(['python', script_name] + list(args), capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error al ejecutar {script_name}: {result.stderr}")
        sys.exit(1)
    logger.info(f"Salida de {script_name}: {result.stdout}")
    return result.stdout

def main():
    # Limpiar el archivo de log
    clear_log_file()
    
    # Si se proporcionan argumentos, los usamos. De lo contrario, pedimos al usuario
    if len(sys.argv) > 1:
        manga_name = sys.argv[1]
        chapters_input = ' '.join(sys.argv[2:4])  # Captura num_capitulo_desde y num_capitulo_hasta si existen
        auto_mode = True
    else:
        manga_name = input("Ingrese el nombre del manga: ")
        chapters_input = input("¿Qué capitulo/s quieres descargar? Si quieres descargar sólo uno en específico, indica el número del capítulo. Si quieres de un capítulo a otro, especifica el número de capítulo desde, espacio, número de capítulo hasta. Si quieres todos, pulsa intro, sin escribir nada más: ")
        auto_mode = False
    
    logger.info(f"Buscando resultados para el manga: {manga_name}")
    
    logger.info("Buscando resultados...")
    results = get_search_results(manga_name)
    
    if not results:
        logger.info("No se encontraron resultados.")
        sys.exit(1)
    
    if auto_mode:
        selected_url = results[0][1]  # En modo automático, seleccionamos siempre el primer resultado
        logger.info(f"Modo automático: Se seleccionó el primer resultado: {selected_url}")
    else:
        logger.info("Resultados encontrados:")
        for idx, url in results:
            logger.info(f"Resultado {idx}: {url}")

        try:
            choice = int(input("Seleccione el número del manga que desea (1-10): "))
            if choice < 1 or choice > 10:
                raise ValueError("Número fuera del rango permitido.")
        except ValueError as e:
            logger.error(f"Entrada inválida: {e}")
            sys.exit(1)

        selected_url = results[choice - 1][1]
        logger.info(f"Manga seleccionado: {selected_url}")

    logger.info(f"El manga que has elegido es {selected_url}.")
    
    logger.info(f"Capítulos seleccionados: {chapters_input if chapters_input else 'Todos los capítulos'}")
    logger.info("Obteniendo lista de capítulos...")

    # Llamar al script get_chapter_url.py con selected_url y manga_name
    run_script('get_chapter_url.py', selected_url)

    # Preparar los argumentos para redirect.py
    get_chapter_args = [selected_url]
    if chapters_input:
        get_chapter_args.extend(chapters_input.split())

    logger.info("Descargando capítulos seleccionados...")
    # Llamar al script redirect.py con get_chapter_args
    run_script('redirect.py', *chapters_input.split())

    logger.info("Proceso completado con éxito.")

if __name__ == '__main__':
    main()
