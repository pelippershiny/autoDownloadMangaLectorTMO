import cloudscraper
import subprocess
import sys
import time

def log_message(message):
    with open("log.txt", "a") as log_file:
        log_file.write(f"{message}\n")

def get_urls_from_script(args):
    log_message(f"Ejecutando get_ref_chapter.py con los argumentos: {args}")
    
    # Llamar al script get_ref_chapter.py con los argumentos proporcionados
    result = subprocess.run(['python', 'get_ref_chapter.py'] + args, capture_output=True, text=True)
    
    # Verificar si el script se ejecutó correctamente
    if result.returncode != 0:
        log_message(f"Error al ejecutar get_ref_chapter.py: {result.stderr}")
        sys.exit(1)
    
    # Leer las URLs del resultado del script y extraer solo las URLs
    urls = result.stdout.splitlines()
    log_message(f"URLs obtenidas: {urls}")
    return urls

def redirect_urls(urls):
    # Crear un scraper para evadir Cloudflare
    scraper = cloudscraper.create_scraper()
    
    # Headers necesarios para la solicitud
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://visortmo.com/library/manga/624/one-piece"
    }

    max_attempts = 10

    for entry in urls:
        # Extraer solo la URL del formato "{titulo} - {capitulo} - {url}"
        *_, upload_url = entry.rsplit(' - ', 2)

        attempt = 0
        while attempt < max_attempts:
            try:
                # Hacer la solicitud a la URL que redirige
                response = scraper.get(upload_url, headers=headers, allow_redirects=True)
                
                # Verificar la URL final después de la redirección
                final_url = response.url

                # Comprobar si la URL final contiene "viewer"
                if "viewer" in final_url:
                    log_message(f"URL final para {upload_url}: {final_url}")
                    print("Redirección exitosa!")
                    
                    # Obtener el título y el capítulo del formato "{titulo} - {capitulo} - {url}"
                    title = entry.split(' - ', 1)[0]
                    chapter = entry.split(' - ')[1]

                    # Llamar al script download_chapter.py con el título, el capítulo y la URL final
                    download_result = subprocess.run(['python', 'download_chapter.py', title, chapter, final_url], capture_output=True, text=True)
                    
                    # Verificar si el script de descarga se ejecutó correctamente
                    if download_result.returncode != 0:
                        log_message(f"Error al ejecutar download_chapter.py: {download_result.stderr}")
                    else:
                        log_message(f"Descarga completada para la URL: {final_url}")
                    
                    break
                else:
                    attempt += 1
                    log_message(f"Intento {attempt}/{max_attempts} fallido. La URL {final_url} no contiene 'viewer'.")
                    if attempt < max_attempts:
                        log_message("Reintentando...")
                    else:
                        log_message(f"No se logró encontrar 'viewer' después de {max_attempts} intentos.")
                
            except Exception as e:
                log_message(f"Excepción al acceder a {upload_url}: {e}")
                attempt += 1
                log_message(f"Intento {attempt}/{max_attempts} fallido.")
                if attempt < max_attempts:
                    log_message("Reintentando...")
                else:
                    log_message(f"No se logró acceder después de {max_attempts} intentos.")
                
            # Esperar 2 segundos antes de hacer la siguiente solicitud
            time.sleep(3)

if __name__ == '__main__':
    # Verificar el número de argumentos
    if len(sys.argv) > 3:
        log_message("Uso incorrecto del script. Se requieren 0, 1 o 2 argumentos.")
        print("Uso: python script.py [<número_principal_inicio> [<número_principal_fin>]]")
        sys.exit(1)
    
    # Obtener los números del argumento
    args = sys.argv[1:]
    
    log_message(f"Argumentos recibidos: {args}")
    
    # Obtener las URLs del script get_ref_chapter.py
    urls = get_urls_from_script(args)
    
    # Redirigir a través de cada URL obtenida
    redirect_urls(urls)
