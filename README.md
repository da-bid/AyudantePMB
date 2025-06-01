# AyudantePMB
Este es un programa escrito en Python para ayudar principalmente a la función del banco de libros. En resumen, lo que permite al utilizarlo es utilizar acciones por lotes, que no hay en el PMB y que dificultan mucho la tarea. Entre las acciones en lote está la creación de grupos automática y la creación de usuarios automática.

Puede funcionar tanto con el PMB online como local, lo único que hace es repetir la misma acción que haría una persona pero mucho más rápido.

En lliurex puede dar error al leer los archivos CSV u otros archivos debido a la codificación, se necesita que la codificación sea utf-8 para que puedan haber caracteres con acentos, etc. En windows ese problema no sucede.

## Requisitos
- Python 3:
    - Windows: https://www.python.org/downloads/
    - Lliurex: `sudo apt install python3`
- Beautiful Soup: `pip install beautifulsoup4`
- ConfigParser: `pip install configparser`

Una vez tengas lo anterior instalado ya podrás abrir el archivo principal `__init__.py`. Si no puedes abrirlo, abre una Consola/Terminal/Powershell en la carpeta y utiliza:
- Windows con CMD (pantalla negra): `python __init__.py`
- Windows con powershell (pantalla azul): `python .\__init__.py`
- Lliurex (Konsole/Terminal/etc): `python3 __init__.py` 

Para abrir la consola:
    - En windows pulsanso `shift`y click con el derecho en un sitio vacío de la carpeta (se abre la powershell)
    - En lliurex haciendo click con el derecho en un sitio dde la carpeta.

## Instrucciones

## Primer uso
1. La primera vez que se abra te preguntará nombre de usuario, contraseña, y código del centro. Estos datos se guardan en el archivo `config.ini` y no salen de tu ordenador.
2. Aparecerá el menú donde podemos: 
    2.1 Crear libros para el banco de libros
    2.2 Eliminar registros enteros de libros o devolver registros enteros de libros.
    2.3 Crear grupos: Dentro hay varias opciones pero la recomendada siempre es `Generar grupos a partir de NIA y nombre del grupo automáticamente`
    2.4 Eliminar nombre y usuario del ordenador: Elimina el archivo `config.ini` que se ha generado en el paso 1.

### Crear grupos
1. Seleccionamos en el menú principal la opción `3) Menú de gestión de grupos` (pulsamos 3 y luego INTRO)
2. A continuación seleccionamos `2) Generar grupos a partir de NIA y nombre del grupo automáticamente`
3. Finalmente `1) Crear de grupos (modificará el PMB creando los grupos)`

El programa buscará un archivo CSV (un Excel guardado como CSV) y dentro de él buscará que una columna tenga como encabezado columna llamada `Grupo` o `Grups` y la otra tenga como encabezado `NIA`. Puede haber más columnas y no afectaría.

4. Si la encuentra nos preguntará `¿Eliminar los grupos existentes antes? (en caso contrario se reutilizan los que están) [S-1 / N-0]`. Si queremos que borre los grupos antiguos (junto con su tutor asociado) le decimos que sí (pulsamos 1 y luego INTRO). Si no queremos que borre los grupos porque tenemos asociados los tutores correctamente le decimos que no.

### Crear libros en lotes (para el banco de libros)
Esta función puede crear rápidamente una gran cantidad de ejemplares para los registros.