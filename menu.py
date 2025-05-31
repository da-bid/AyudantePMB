import os

def mostrar_menu(opciones):
    print('Seleccione una opción:')
    for clave in sorted(opciones):
        print(f' {clave}) {opciones[clave][0]}')


def leer_opcion(opciones):
    while (a := input('Opción: ')) not in opciones:
        print('Opción incorrecta, vuelva a intentarlo.')
    return a


def ejecutar_opcion(opcion, opciones):
    opciones[opcion][1]()


def generar_menu(opciones, opcion_salida):
    opcion = None
    msg=""
    if "msg" in opciones.keys():
        opcion_salida=str(int(opcion_salida)-1)
        msg=opciones["msg"]
        del opciones["msg"]
    while opcion != opcion_salida:
        os.system('cls||clear')
        if msg !="": print (msg)
        mostrar_menu(opciones)
        opcion = leer_opcion(opciones)
        ejecutar_opcion(opcion, opciones)
        print()

def void():
    pass