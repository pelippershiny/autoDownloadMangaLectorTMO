import csv
import re
import sys
import logging

# Configurar el logging para que escriba en log.txt
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_max_chapter():
    # Leer el archivo CSV y obtener el número del capítulo de la segunda fila
    try:
        with open('result.csv', 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader, None)  # Omitir la cabecera
            second_row = next(csv_reader, None)  # Tomar la segunda fila
            if second_row:
                match = re.match(r'^Capítulo (\d+)\.(\d+)', second_row[0])
                if match:
                    max_chapter = match.group(1)  # Tomar el número del capítulo principal
                    logging.info(f"Máximo capítulo encontrado: {max_chapter}")
                    return int(max_chapter)  # Convertir a entero
    except Exception as e:
        logging.error(f"Error al leer el archivo CSV: {e}")
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)
    return None

def search_csv(start_number=None, end_number=None):
    # Leer el archivo CSV y almacenar los datos en una lista
    data = []
    try:
        with open('result.csv', 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            
            # Omitir la cabecera
            next(csv_reader, None)
            
            # Almacenar los datos
            for row in csv_reader:
                if len(row) >= 3:
                    chapter_text = row[0]
                    link_url = row[1]
                    title = row[2]
                    data.append((title, chapter_text, link_url))
        logging.info(f"Datos leídos correctamente desde result.csv")
    
    except FileNotFoundError:
        logging.error("El archivo result.csv no se encuentra.")
        print("El archivo result.csv no se encuentra.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error al leer el archivo CSV: {e}")
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)

    # Variable para rastrear si ya se imprimió algo
    printed_once = False

    if start_number is None:
        # Si no se pasa ningún número, devolver todas las URLs una sola vez
        logging.info("No se especificaron números, devolviendo todas las URLs.")
        for title, chapter_text, link_url in data:
            print(f"{title} - {chapter_text} - {link_url}")
        printed_once = True  # Marcar que ya se imprimió

    elif end_number is None:
        # Si solo se pasa un número, buscar capítulos con ese número principal
        pattern = re.compile(rf'^Capítulo {start_number}\.\d+')
        logging.info(f"Buscando capítulos con el número principal {start_number}")

        start_main_number, start_decimal = int(start_number), 0
        end_main_number, end_decimal = int(start_number), 99

        def is_in_range(chapter_number, chapter_decimal, start_main, start_decimal, end_main, end_decimal):
            return (chapter_number == start_main and chapter_decimal >= start_decimal)

    else:
        # Si se pasan dos números, buscar capítulos en el rango
        pattern = re.compile(rf'^Capítulo ({start_number}\.\d+|{end_number}\.\d+|{start_number}|{end_number})')
        logging.info(f"Buscando capítulos en el rango {start_number} - {end_number}")

        def is_in_range(chapter_number, chapter_decimal, start_main, start_decimal, end_main, end_decimal):
            return (chapter_number > start_main or (chapter_number == start_main and chapter_decimal >= start_decimal)) and \
                   (chapter_number < end_main or (chapter_number == end_main and chapter_decimal <= end_decimal))
        
        start_main_number, start_decimal = int(start_number), 0
        end_main_number, end_decimal = int(end_number), 99  # Asegurar que end_number sea un entero

    # Solo imprimir si no se ha hecho antes
    if not printed_once:
        # Iterar sobre los datos almacenados
        for title, chapter_text, link_url in data:
            # Extraer el número principal y el número decimal del capítulo
            match = re.match(r'^Capítulo (\d+)\.(\d+)', chapter_text)
            if match:
                chapter_main_number, chapter_decimal_number = match.groups()
                chapter_number = int(chapter_main_number)
                chapter_decimal = int(chapter_decimal_number)
                
                # Comprobar si el capítulo está en el rango especificado
                if (start_number is None) or is_in_range(chapter_number, chapter_decimal, start_main_number, start_decimal, end_main_number, end_decimal):
                    logging.info(f"Capítulo encontrado: {title} - {chapter_text} - {link_url}")
                    print(f"{title} - {chapter_text} - {link_url}")

if __name__ == '__main__':
    # Verificar el número de argumentos
    if len(sys.argv) > 3:
        logging.error("Uso incorrecto del script. Se requieren 0, 1 o 2 argumentos.")
        print("Uso: python script.py [<número_principal_inicio> [<número_principal_fin>]]")
        sys.exit(1)

    # Obtener los números del argumento
    start_number = sys.argv[1] if len(sys.argv) > 1 else None

    # Si se pasa "MAX", obtener el número del capítulo de la segunda fila
    if len(sys.argv) == 3 and sys.argv[2] == "MAX":
        end_number = get_max_chapter()  # Obtener el número máximo de capítulo
    else:
        end_number = sys.argv[2] if len(sys.argv) == 3 else None
    
    logging.info(f"Argumentos recibidos: start_number={start_number}, end_number={end_number}")
    
    # Realizar la búsqueda
    search_csv(start_number, end_number)
