# autoDownloadMangaLectorTMO

Este proyecto te permite descargar mangas automáticamente desde el sitio visortmo.com.

## Instrucciones de Uso

### 1. Modificar `options.json`

Antes de empezar, modifica el archivo `options.json` para definir la ruta en la que deseas que se descarguen los mangas. Usa el siguiente formato:

```
"Ruta\Manga\Descargas\"
```

Si no se especifica una ruta, los mangas se descargarán en la ubicación actual donde se ejecuta el script.

### 2. Ejecutar el script de descarga

Tienes dos opciones para ejecutar el script:

#### 2.1. Ejecución interactiva

Ejecuta el archivo `descargaManga.bat` y sigue los pasos que se te piden por pantalla para buscar y descargar mangas.

#### 2.2. Ejecución directa con parámetros

Si prefieres omitir los diálogos interactivos, puedes ejecutar el script pasando directamente los parámetros correspondientes:

- Para descargar un solo capítulo del manga:
    ```
    python get_manga.py "Nombre Manga" {capitulo}
    ```
    Ejemplo: 
    ```
    python get_manga.py "One Piece" 10
    ```

- Para descargar un rango de capítulos:
    ```
    python get_manga.py "Nombre Manga" {capituloInicio} {capituloFin}
    ```
    Ejemplo: 
    ```
    python get_manga.py "One Piece" 10 20
    ```

- Para descargar desde un capítulo específico hasta el final:
    ```
    python get_manga.py "Nombre Manga" {capituloInicio} MAX
    ```
    Ejemplo: 
    ```
    python get_manga.py "One Piece" 200 MAX
    ```

- Para descargar todos los capítulos disponibles de un manga:
    ```
    python get_manga.py "Nombre Manga"
    ```
    Ejemplo: 
    ```
    python get_manga.py "One Piece"
    ```

¡Disfruta descargando tus mangas favoritos!
