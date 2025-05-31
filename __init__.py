# Nombre del programa: AyudantePMB
# Versión: 1.0
# Autor: David Palazón.
# Repositorio: https://github.com/da-bid/AyudantePMB
# 
# Este software se proporciona "tal cual", sin garantías de ningún tipo. Para más detalles,
# consulta la licencia GPLv3 en https://www.gnu.org/licenses/gpl-3.0.html.



from collections import defaultdict
import configparser
from blman import blman
from menu import *
import os

configFileName='config.ini'
config=configparser.ConfigParser()

def menu_principal():
    opciones = {
        '1': ('Menú de creación de libros', submenuCreaLib),
        '2': ('Menú de eliminación/devolución de libros', submenuBorraLib),
        '3': ('Menú de gestión de grupos', submenuGrupos),
        '4': ('Borrar el nombre de usuario y la contraseña de este ordenador',borrarDatos),
        '5': ('Salir', bl.salir)
    }
    generar_menu(opciones, str(len(opciones)) )

def submenuCreaLib():
    opciones = {
        'msg': """En la primera opción generaremos una lista de los libros que queremos crear. Si nos equivocamos podemos eliminarlo con la segunda opción. Cuando acabemos comprobamos que no haya ningún error (opción 3 del menú). Y, por último, si todo está bien crearemos los libros con la opción 4, se generará una carpeta llamada ETQ con los PDF de las etiquetas DESPUÉS de acabar una asignatura y un archivo llamado 'etiquetas.txt' de respaldo con los números de las etiquetas MIENTRAS se están generando.
        
ATENCIÓN: Se recomienda que se ponga como configuración POR DEFECTO la que queramos para los libros del banco de libros""",
        '1': ('Añadir/modificar un libro al listado de creación de libros', addBooks),
        '2': ('Eliminar un libro de listado de libros', elimBooks),
        '3': ('Ver listado de libros que se van a crear', listBooks),
        '4': ('Crear los libros que se han añadido', bl.cLibros),
        '5': ('Salir', void)
           }
    generar_menu(opciones, str(len(opciones)))

def submenuBorraLib():
    opciones = {
        'msg': "Sólo se pueden borrar los libros si ya han sido devueltos, por ello primero deberás devolver todos los libros y después borrarlo.",
        '1': ('Devolver todos los libros de un registro', bl.devTodo),
        '2': ('Eliminar todos los libros de un registro y el registro', bl.delTodo),
        '3': ('Salir', void)
    }
    generar_menu(opciones,str(len(opciones)))

def submenuGrupos():
    opciones ={
        'msg': "Para crear los grupos tendremos que eliminar los existentes (opción 1 del menú) y posteriormente generar los actuales. Para generar los actuales podemos usar un archivo CSV con la ID del alumno y la ID del grupo (opción 2), esta manera es más óptima pero tendremos que calcular en una hoja de cálculo. O bien generar los grupos a partir del CSV de matrícula (no tiene por qué estar completo), esta opción es mucho menos óptima y no funcionará bien con los PDC",
        '1': ('Generar grupos a partir de ID (manual)', submenGruposManual),
        '2': ('Generar grupos a partir de NIA y nombre del grupo automáticamente', submenGruposAutomático),
        '3': ('Salir', void)
    }
    generar_menu(opciones,str(len(opciones)))

def submenGruposManual():
    opciones ={
        'msg': "Para obtener un listado de ID de alumnos deberás ir en el PMB a Informes->Usuario actuales y crear una cesta de alumnos. Despues en Circulación -> Cestas -> Gestión -> En la cesta que hemos creado pulasmos Acciones -> Ediciones -> Archivo EXCEL",
        '1': ('Vaciar grupos', bl.gVaciarGrupos),
        '2': ('Generar listado de ID de grupos',bl.gSaveCSVGrupos),
        '3': ('Generar listado de ID de alumnos', gSaveCSVUsersIDAction),
        '4': ('Crear grupos a partir de un CSV con IDs', bl.gGroupCreator),
        '5': ('Salir', void)
    }
    generar_menu(opciones,str(len(opciones)))

def gSaveCSVUsersIDAction():
    bl.gSaveCSVUsersID(bl.gGetUsersID())

def submenGruposAutomático():
    opciones ={
        'msg': """El programa buscará en su carpeta un CSV llamado "Matrícula Curso escolar 202X-202Y.csv", "Matrícula Curs escolar 202X, 202Y.csv" (archivos que genera ITACA) o "NIAGRUPO.csv". Dentro buscará una columna llamada Grupo o Grups y otra llamada NIA.""",
        '1': ('Crear de grupos (modificará el PMB creando los grupos)', bl.gGroupCreatorFromNIA),
        '2': ('Salir', void)
    }
    generar_menu(opciones,str(len(opciones)))


def addBooks():
    os.system('cls||clear')
    global listado
    listado = bl.loadBookFile()
    if listado is None: listado={}
    menu=True
    while menu:
        bucle=True
        while bucle:
            print("""Indica el ID del libro que quieres añadir o modificar de la lista de creación
    (para ello puedes abrir el registro de un libro y al final de la URL verás un número, esa es la ID)""")
            id= input()
            if id=="": menu=False; break;
            if id.isnumeric(): 
                id=int(id)
                if bl.isValidReg(id)==True:
                    bucle=False
                else:
                    print ("No se ha encontrado ese libro en el PMB")
        bucle=True
        while bucle and menu:
            signatura= bl.getSignatura(id)
            if signatura != "":
                print('La signatura detectada es %s, pulsa INTRO para aceptarla o escribe una nueva:' %signatura)
                aux= input("Signatura:")
            else:
                print("No se ha detectado ninguna signatura utilizada ya. Introduzca una signatura:")
                aux= input("Signatura:")
            if aux != "": signatura = aux
            bucle=False
        bucle=True
        while bucle and menu:
            print ('Indica cuantos ejemplares deseas crear de este libro')
            ncopias = input()
            if ncopias =="false": menu=False; break
            if ncopias.isnumeric(): ncopias=int(ncopias); bucle=False
        if menu==False: break
        if not id in listado.keys():listado[id]={}
        listado[id]["s"]=signatura
        listado[id]["nc"]=ncopias
        
        bucle=True
        bl.saveBookFile(listado)
        print("¿Creamos otro libro más? [S-1/N-0]")
        ans=input()
        if ans.lower()=="n" or ans==str(0):break
            

def listBooks():
    os.system('cls||clear')
    l=bl.loadBookFile()
    if l is None:
        print ("No hay libros en la lista")
        return
    print ("Lista libros")
    print ('|%-12s' %"ID", '|%-30s' %"SIGNATURA", '|%-12s' %"N.COPIAS","|")
    print ("|","-"*11,"|","-"*29,"|","-"*11,"|")

    for i in l.keys():
        if l[i]["s"]=="": bl.getSignatura(i)
        print ('|%-12s' %i, '|%-30s' %l[i]["s"], '|%-12s' %l[i]["nc"],"|")
    input("Pulsa INTRO para volver al menú")

def elimBooks():
    id = input()
    bucle=True
    while bucle:
        print ('Introduce el ID del libro que quieres eliminar')
        id= input()
        if id=="": break;
        if id.isnumeric(): 
            id=int(id)
            try:
                del listado[id]
            except:
                print ("No se ha encontrado ese libro en el listado")

def borrarDatos():

    arrElim=[
        ['¿Desea borrar la configuración (nombre de usuario, contraseña, código del centro) del programa?[S-1 / N-0]',configFileName],
        ['¿Desea el listado de libros pendientes de creacion (no borrará ninguna etiqueta)?', bl.BookFileName],
        ['¿Desea borrar el listado de grupos? [S-1/N-0]', bl.GroupListFileName],
        ['¿Desea borrar el listado de NIA e ID? [S-1/N-0]', bl.GroupCreatorUsersID]
    ]
    print('¿Desea borrar TODOS los archivos con información salvo las etiquetas? [S-1 / N-0]')
    ans=input()
    if ans.lower() =='s' or ans=="1":
        for x in arrElim:
            try:
                os.remove(x[1]) #Borra
            except:
                print ("No se ha podido borrar "+x[1])
    else:
        for x in arrElim:
            print(x[0]) #Pregunta al usuario si desea borrar
            ans=input()
            if ans.lower() =='s' or ans=="1":
                try:
                    os.remove(x[1]) #Borra
                except:
                    print('No había ningún archivo que borrar')
                    pass
   

if __name__ == '__main__':
    bucle=True
    datosnuevos=False
    bl=blman ()
    while bucle:
        try:
            with open(configFileName,'r',encoding='utf-8') as f:
                f.close()
            config.read(configFileName)
        except:
            print ("""Es la primera vez que se ejecuta el programa por lo que se va a generar un archivo de configuración junto al programa para recordar los datos. Puedes eliminar este archivo en cualquier momento""")
            print ("Indica el usuario")
            config["DEFAULT"]["usu"]=input()
            print ("Indica la contraseña")
            config["DEFAULT"]["pass"]=input()
            print ("Si usas el PMB online pon el código del centro, si usas el local déjalo en blanco")
            config["DEFAULT"]["cc"]=input()
            if config["DEFAULT"]["cc"]=="":
                print ("Si usas el local indica el dominio. O simpelmente pulsa intro para utilizar http://pmb/")
                config["DEFAULT"]["dom"]=input()
                if config["DEFAULT"]["dom"]=="": config["DEFAULT"]["dom"]="http://pmb/"
            else:
                config["DEFAULT"]["dom"]="https://pmb.edu.gva.es/"
            datosnuevos=True

        bl.user=config['DEFAULT']["usu"]
        bl.pwd=config['DEFAULT']["pass"]
        bl.cCentro=config["DEFAULT"]["cc"]
        bl.dominio=config['DEFAULT']["dom"]

        if bl.reconnect()==True:
            bucle=False
            if datosnuevos:
                with open(configFileName, 'w',encoding='utf-8') as configfile:
                    config.write(configfile)
                    configfile.close()
        else:
            print ("Error en la configuración (usuario, contraseña, dominio o código de centro). Vuelva a introducir los datos")
            try:
                os.remove(configFileName) #Borra
            except:
                pass
    print ("""
Bienvenido al Ayudante del Banco de Libros (ABL).
ADVERTENCIA:
1) Se recomienda hacer una copia de seguridad porque las acciones que aquí realices no se pueden deshacer.
2) Revisa en el PMB las acciones efectuadas tras realizar el trabajo para comprobar que es correcto. Si se detectara algun tipo de error simplemente restaura copia de seguridad de la base de datos anterior.

Se ha iniciado sesión en:  """ + bl.dominio)
    input("Pulsa cualquier INTRO para continuar")
    menu_principal()