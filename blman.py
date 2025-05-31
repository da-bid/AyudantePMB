# Nombre del programa: AyudantePMB API
# Versión: 1.0
# Autor: David Palazón.
# Repositorio: https://github.com/da-bid/AyudantePMB
# 
# Este software se proporciona "tal cual", sin garantías de ningún tipo. Para más detalles,
# consulta la licencia GPLv3 en https://www.gnu.org/licenses/gpl-3.0.html.


import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

def merge_two_dicts(a, b):
    z = a.copy()
    z.update(b)
    return z

def remDuplicate(lista,key):
    auxl=[]
    for x in lista:
        if not x[key] in auxl: auxl.append(x[key])
    auxl.sort()
    return auxl

class blman:
    def __init__(self, user="", pwd="",dominio="",cCentro=""):
        self.BookFileName="ListLib.csv"
        self.GroupListFileName="ListaGrupos.csv"
        self.GroupCreatorCSV="Grupos.csv"
        self.GroupCreatorUsersID='usersID.csv'
        self.MatriculaCSVfilename="NIAGRUPO.csv"

        self.user=user
        self.pwd=pwd
        self.cCentro=cCentro
        self.dominio=dominio
        self.version=20
        self.Connected=False
        self.path=None

        self.dictNIA2ID={}
        self.dictGrupo={}
        self.s = requests.Session()
        
  
    def reconnect(self, force=False):
        if self.Connected==False or force:
            payload = {'user': self.user,'password': self.pwd}
            print ("Iniciando sesión en PMB..... Espere.")
            if self.cCentro !="": self.s.get(self.dominio+'index.php?codcentro='+self.cCentro, allow_redirects = True)
            try:
                r = self.s.post(self.dominio+'main.php', data=payload, allow_redirects = True)
            except:
                return False 
            if "<h4 class='erreur'>Identificación incorrecta</h4>" in r.text or r.status_code!=200:
                print ("Error al conectar, posiblemente el usuario o la contraseña sea incorrecta.")
                return False
            else:
                print ("Conectado al PMB")
                self.Connected=True
                return True


    def loadBookFile(self):
        try:
            f=open(self.BookFileName,"r",encoding='utf-8')
        except:
            return None
        listado={}
        texto=f.read()
        texto=texto.splitlines()
        for x in texto:
            aux=x.split(";")
            id=int(aux[0].strip())
            listado[id]={}
            listado[id]["nc"]=aux[1].strip()
            try:
                listado[id]["s"]=aux[2].strip()
            except:
                listado[id]["s"]=""
        return (listado)
    
    def isValidReg(self,id):
        self.reconnect()
        r= self.s.get(self.dominio+"catalog.php", params={"id": id})
        return ""!=BeautifulSoup(r.text, 'html.parser').find("h3",{"class":"section-record-title"}).text.strip()
    
    def saveBookFile(self,l):
        f= open(self.BookFileName,"w",encoding='utf-8')
        salida=[]
        for i in l.keys():
            if i=="":continue
            salida.append(str(i)+ ";" + str(l[i]["nc"]) + ";" + l[i]["s"] )
        salida="\n".join(salida)
        f.write(salida)
        f.close()

    def getSignatura(self, id):
        self.reconnect()
        r= self.s.get(self.dominio+"catalog.php", params={"id": id})
        soup = BeautifulSoup(r.text, 'html.parser')
    
        signatura=None
        try:
            signatura=soup.find("td", {"class":"expl-column-1"}).text
        except:
            try:
                arrFilas=soup.findAll('tr')
                col=-1
                fila=-1
                for i in range (0,50):
                    if arrFilas[i].text.find("Signatura") >=0:
                        arrCeldas=arrFilas[i].findAll('th')
                        for j in range (0,50):
                            if arrCeldas[j].text.find("Signatura")>=0:
                                fila = i+1
                                col=j
                                break
                        break
                signatura=arrFilas[fila].findAll('td')[col].text
            except:
                pass

        f= open("ans.html",'w',encoding='utf-8'); f.write(r.text); f.close()
        print (signatura)
       
        if signatura is None:
            return ""
        else:
            return signatura
        
    def html2Payload(self,r):
        soup = BeautifulSoup(r.text, 'html.parser')
        payload={}
        for a in soup.find_all("select"):
            nam=a["name"]
            form_tags=["f_ex_typdoc", "f_ex_nbparts","f_ex_location","f_ex_section8","f_ex_section10", "f_ex_section1", "f_ex_section7", "f_ex_section2", "f_ex_owner", "f_ex_statut", "f_ex_cstat", "f_ex_note", "f_ex_comment", "f_ex_prix", "origine[]", "date_acquisition[]", "Convocatoria[]", "date_pilon[]"]
            if not nam in form_tags: continue
            ele=a.find_all('option', {"selected":"selected"})
            val=""
            for b in ele:
                if b is not None : val = b.get("value"); break
            if val!="": payload[nam]=val
        return payload
        
    def getPayload(self,id):
        self.reconnect()
        r= self.s.get(self.dominio+"catalog.php", params={"id": id})
        soup = BeautifulSoup(r.text, 'html.parser')
        signatura=soup.find("a")
        for a in soup.find_all('a'):
            if ('catalog.php?categ=edit_expl&id='+str(id)+'&cb=') in a["href"]:
                #print (a["href"])
                r= self.s.get(self.dominio+a["href"][1:])
                break
        return self.html2Payload(r)

    def prtT(self,arrCodBrr,filename):
        self.reconnect()
        listCodBrr=','.join(arrCodBrr)
        params={"codigos":listCodBrr, "percentaje_combobox":"1"}
        bucle=True
        while bucle:
            try:
                r = self.s.get(self.dominio+'tejuelo.php', params=params)
                bucle=False
            except:
                self.reconnect(True)

        #Creamos subcarpeta ETQ
        try:
            os.makedirs("ETQ")
        except FileExistsError:
            # directory already exists
            pass
        
        #Creamos subcarpeta para ese día
        if self.path is None: 
            parentfolder=datetime.now().strftime("%Y%m%d")
            i=0
            while True:
                try:
                    if i==0: 
                        self.path="ETQ/"+parentfolder
                    else:
                        self.path= "ETQ/"+parentfolder+" v"+str(i)
                    os.makedirs(self.path)
                    break
                except:
                    i+=1


        with open("./"+ self.path + "/" + filename + ".pdf","wb") as f:
            f.write(r.content)
            f.close()

    def CrearLibro(self, ID,signatura,regPayload):
        self.reconnect()
        bucle=True
        while bucle:
            try:
                r= self.s.post(self.dominio+"catalog.php", params={"categ": "expl_create", "id": ID}, data={"noex": None, "option_num_auto": "num_auto"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
                soup = BeautifulSoup(r.text, 'html.parser')
                cBarr = soup.find("input", {'id': 'f_ex_cb'}).get("value")
                try:
                    idform = soup.find("input", {'name': 'id_form'}).get("value")
                except:
                    idform =""
                payload = {
                    "f_ex_cb": cBarr,
                    "f_ex_cote": signatura,
                    "id_form": idform
                }
                if idform =="": del payload["id_form"]
                payload=merge_two_dicts(payload, self.html2Payload(r))
                payload=merge_two_dicts(payload, regPayload)
                #print (payload)
                r= self.s.post(self.dominio+"catalog.php", params={"categ": "expl_update","sub":"create", "id": ID}, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
                bucle=False
            except:
                self.reconnect(True)
        return cBarr

    def cLibros(self):
        
        listGlobalEj=[]
        listado= self.loadBookFile()

        #Contamos el número de libros que hay para hacer la cuenta atrás
        self.nlibrosprogress=0
        for i in listado.keys():
            self.nlibrosprogress+=int(listado[i]["nc"])
        for ID in list(listado.keys()):
            signatura=listado[ID]["s"]
            while signatura =="":
                signatura=self.getSignatura(ID)
                if signatura !="":break
                print ("Introduzca una signatura para el libro con ID ",ID)
                signatura=input()
            numCopias=listado[ID]["nc"]
            regPayload=self.getPayload(ID)
            list_nejem=[]
            with open("etiquetas.txt", "a",encoding='utf-8') as f:
                f.write("\n"+signatura + "\n")
            
                for i in range (0,int(numCopias)):
                    nejem=self.CrearLibro(ID,signatura,regPayload)
                    list_nejem.append(nejem)
                    f.write(nejem + ", ")
                    print("/n", end="\r", flush=True)
                    print(signatura, ":", i+1,"/",numCopias, "Falta por crear:",self.nlibrosprogress-1, "   ", end="\r", flush=True)
                    self.nlibrosprogress-=1
            
                f.write("\n")
                f.close()
            print ('\n')
            
            self.prtT(list_nejem,signatura)
            
            del (listado[ID])
            self.saveBookFile(listado)
            listGlobalEj+=list_nejem
        self.prtT(listGlobalEj,"Todas")

    def getAllCBar(self,id):
        self.reconnect()
        r= self.s.get(self.dominio+"catalog.php", params={"id": id})
        soup = BeautifulSoup(r.text, 'html.parser')
        colCBar=soup.find_all("td",{"class":"expl-column-0"})
        arrReturn=[]
        for c in colCBar:
            try:
                arrReturn.append(c.text)
            except:
                pass
        return arrReturn

    def delTodo(self):
        self.reconnect()
        print("Indica el ID del registro para ELIMINAR. Déjelo en blanco para salir del MENÚ")
        id=input()
        if id=="":return
        signatura= self.getSignatura(id)
        print("¿Está seguro de que desea eliminar "+ signatura + " ? [S-1/N-0]")
        ans=input()
        if ans.lower()!="s" and ans!=str(1): return
        if self.isValidReg(id)==True:
            bucle=False
        else:
            print ("No se ha encontrado ese libro en el PMB. Pulsa una tecla para continuar")
            input()
            return
        print ("Borrando.....")
        i=0
        numbarritas=50
        todosCbar=self.getAllCBar(id)
        for i in range(len(todosCbar)):
            r = self.s.get(self.dominio+"catalog.php?categ=del_expl&cb="+todosCbar[i]) #eliminar
            parte=int(numbarritas*i/len(todosCbar))
            print ("[", "="*parte, " "*(numbarritas-parte-1), "]           ", end="\r")
        r = self.s.get(self.dominio+"catalog.php?&categ=delete&id="+str(id)) #eliminar registro
        input("Borrado, pulsa INTRO para continuar")

    def devTodo(self):
        self.reconnect()
        print("Indica el ID del registro para devolver todos los libros")
        id=input()
        signatura= self.getSignatura(id)
        if signatura !="":
            bucle=False
        else:
            print ("No se ha encontrado ese libro en el PMB. Pulsa una tecla para continuar")
            input()
            return
        if id=="":return
        print ("Devolviendo.....")
        for libro in self.getAllCBar(id):
            r = self.s.get(self.dominio+"circ.php?categ=retour&form_cb_expl="+libro) #devolver
        input("Todos los préstamos devueltos, pulsa INTRO para continuar")   


    #Esta función devuelve un dict donde las keys son el nombre del grupo y el valor de dentro la ID del grupo
    def gGetGroupsID(self):
        self.reconnect()
        r = self.s.get(self.dominio+"circ.php?categ=groups&action=listgroups&groups_ui_nb_per_page=999")

        soup = BeautifulSoup(r.text, 'html.parser')
        arrFila=soup.find_all('td', {"class":"list_ui_list_cell_content groups_ui_list_cell_content_libelle"})
        self.dictGrupo={}
        for celda in arrFila:
            x = re.search(r'groupID=(\d+)\"', celda["onclick"])
            if x == None: continue
            self.dictGrupo[celda.text]=x.group(1)
        return self.dictGrupo

            
        return self.dictGrupo
    
    def gSaveCSVGrupos(self):
        dictGrupo=self.gGetGroupsID()
        f= open(self.GroupListFileName,"w",encoding='utf-8')
        salida=[]
        for i in dictGrupo.keys():
            salida.append(i+ ";" + str(dictGrupo[i]))
        salida="\n".join(salida)
        f.write(salida)
        f.close()
        

    def gGetUsersID(self):
        self.reconnect()
        if self.dictNIA2ID!={}:
            ans=""
            while not (ans.lower()=="s" or ans=='1' or ans.lower()=="n" or ans=='0'):
                print ("Ya se han obtenido los ID de los usuarios en esta sesión. ¿Reutilizamos los datos? [S-1/N-0]")
                ans=input()
                if ans.lower()=="s" or ans==str(1): return self.dictNIA2ID
        r = self.s.get(self.dominio+"edit.php?categ=empr&sub=encours&readers_edition_ui_nb_per_page=9999")
        arrMatch=re.findall(r"""\".\/circ\.php\?categ=pret&form_cb=(\d+)\"""", r.text)
        r = self.s.get(self.dominio+"edit.php?categ=empr&sub=encours&readers_edition_ui_nb_per_page=9999&empr_categ_filter=7")
        arrMatchProfes=re.findall(r"""\".\/circ\.php\?categ=pret&form_cb=(\d+)\"""", r.text)
        self.dictNIA2ID={}
        print ("Buscando ID de cada NIA....")
        for i in range(len(arrMatch)):
            if arrMatch[i] in self.dictNIA2ID.keys():continue
            numbarritas=50
            parte=int(numbarritas*i/len(arrMatch))
            print ("[", "="*parte, " "*(numbarritas-parte-1), "]           ", end="\r")
            bucle=True
            while bucle:
                try:
                    r = self.s.get(self.dominio+"circ.php?categ=pret&form_cb="+arrMatch[i])
                    bucle=False
                except:
                    self.reconnect(True)
            x = re.search(r"\'\./circ\.php\?categ=empr_saisie&id=(\d+)", r.text)
            if x == None: continue
            if arrMatch[i] in arrMatchProfes:
                self.dictNIA2ID[arrMatch[i]]={"ID":x.group(1), "CAT":"P"}
            else:
                self.dictNIA2ID[arrMatch[i]]={"ID":x.group(1), "CAT":"A"}

            #print ("Modo debug, no realizará todos los grupos");
            #if i>20: break
        return self.dictNIA2ID

    def gGetDataFromMatriculaCSV(self):
        pathfiles= os.listdir()
        print ("Buscando archivos CSV...")
        file=pathfiles[0]
        for file in pathfiles:
            if file.lower().endswith(".csv"):
                print (file)
                if file.startswith(self.MatriculaCSVfilename): break
                if file.lower().startswith("matrícula curs escolar"): self.MatriculaCSVfilename = file; break
                if file.lower().startswith("matrícula curso escolar"): self.MatriculaCSVfilename = file; break
                if file.lower().startswith("grup"): self.MatriculaCSVfilename = file; break
        print ("Archivo %s encontrado" %self.MatriculaCSVfilename)
        data=""
        try:
            file=open(self.MatriculaCSVfilename, 'r',encoding='utf-8')
            data = file.read()
            file.close()
        except:
            file=open(self.MatriculaCSVfilename, 'r')
            data = file.read()
            file.close()
        
        if data=="":
            print ("Error al leer el %s no encontrado" %self.MatriculaCSVfilename)
            input ("Pulsa INTRO para continuar")
            return []

        data=data.splitlines()
        encabezado=data.pop(0).replace(";",",").split(",")
        pnia=-1
        pgrupo=-1
        pcurs=-1
        arrNIAgrupo=[]
        for i in range(len(encabezado)):
            if str(encabezado[i]).lower().find("nia") >=0: pnia=i
            if str(encabezado[i]).lower().find("curs") >=0: pcurs=i
            if str(encabezado[i]).lower().find("grup") >=0: pgrupo=i

        #Falla al encontrar el índice de la columna del NIA y del grupo¿?
        for linea in data:
            x=linea.replace(";",",").split(",")
            if pgrupo ==-1 and pcurs==-1: continue
            if pcurs!=-1 and x[pcurs].find("PDC")>=0:
                arrNIAgrupo.append([x[pnia], x[pcurs]])
            else:
                arrNIAgrupo.append([x[pnia], x[pgrupo]])
        return arrNIAgrupo
    
    def gGroupCreatorFromNIA(self):
        arrNiaGroup=self.gGetDataFromMatriculaCSV()
        try:
            print("NIA ",arrNiaGroup[0][0]," será asociado con grupo ", arrNiaGroup[0][1])
        except:
            input("Error al leer el archivo de matrícula. Pulsa INTRO para continuar.")
            return
        if arrNiaGroup==[]: return
        dictNia2ID=self.gGetUsersID()
        self.gSaveCSVUsersID(dictNia2ID)
        uniqueGroup=remDuplicate(arrNiaGroup,1)
        print("¿Eliminar los grupos? (en caso contrario se reutilizan los que están) [S-1 / N-0]")
        ans=input()
        if ans.lower()=="s" or ans==str(1):
            self.gEliminarGrupos()
            self.gCrearGrupos(uniqueGroup)
        print ("Obteniendo ID de los grupos")
        dictGroup2ID=self.gGetGroupsID()
        arrIDUserGroup=[]
        for prof in dictNia2ID.keys():
            if dictNia2ID[prof]["CAT"]=="P" and "PD" in dictGroup2ID.keys():
                arrIDUserGroup.append([dictNia2ID[prof]["ID"],dictGroup2ID["PD"]])
            
        for line in arrNiaGroup:
            try:
                arrIDUserGroup.append([dictNia2ID[str(line[0])]["ID"],dictGroup2ID[str(line[1])]])
            except:
                print ("Error: Usuario "+line[0]+"del grupo "+line[1]+" no encontrado en el PMB")
        print ("Enlazando alumnos a los grupos....")
        for i in range(len(arrIDUserGroup)):
            numbarritas=80
            parte=int(numbarritas*i/len(arrIDUserGroup))
            print ("[", "="*(parte+1), " "*(numbarritas-parte-1), "]           ", end="\r")
            bucle=True
            while bucle:
                try:
                    r=self.s.get(self.dominio+"circ.php?categ=groups&action=addmember&groupID="+arrIDUserGroup[i][1]+"&memberID="+arrIDUserGroup[i][0])
                    bucle=False
                except:
                    self.reconnect(True)
        input ("Grupos creados. PULSA INTRO PARA CONTINUAR")

    def gSaveCSVUsersID(self,dictNIA2ID):
        f=open(self.GroupCreatorUsersID,'w',encoding='utf-8')
        #self.dictNIA2ID=self.gGetUsersID()
        finalstring=""
        for x in dictNIA2ID.keys():
            line=';'.join([x,dictNIA2ID[x]["ID"]])
            finalstring="\n".join([finalstring,line])
        f.write(finalstring)
        f.close

    def gVaciarGrupos(self):
        self.reconnect()
        dictGrupo=self.gGetGroupsID()
        for grupo in dictGrupo.keys():
            print ("Eliminando ", grupo, end="\r")
            r = self.s.get(self.dominio+"circ.php?categ=groups&action=showgroup&groupID="+dictGrupo[grupo])
            arrMatch = re.findall(r"""href=\".\/(circ.php\?categ=groups&action=delmember&groupID="""+dictGrupo[grupo]+r"""&memberID=\d+)\"""", r.text)
            for i in range(len(arrMatch)):
                self.s.get(self.dominio+arrMatch[i])
                parte=int(12*i/len(arrMatch))
                print ("Eliminando ", grupo, "[", "="*parte, " "*(12-parte), "]           ", end="\r")
            #self.s.get(self.dominio+"circ.php?categ=groups&action=update&group_name="+grupo+"&libelle_resp=&comment_gestion=&comment_opac=&respID=0&groupID="+dictGrupo[grupo])

    def gEliminarGrupos(self):
        self.reconnect()
        dictGrupo=self.gGetGroupsID()
        print ("Eliminando grupos....")
        for grupo in dictGrupo.keys():
            r = self.s.get(self.dominio+"circ.php?categ=groups&action=delgroup&groupID="+dictGrupo[grupo])
        print ("Grupos eliminados")

    def gCrearGrupos(self,listGrupos):
        listGrupos.append("PD")
        self.reconnect()
        for grupo in listGrupos:
            r = self.s.get(self.dominio+"circ.php?categ=groups&action=update&group_name="+grupo)


    def gGroupCreator(self):
        self.reconnect()
        print("¿Hay un archivo en la carpeta llamado "+ self.GroupCreatorCSV + " cuya primera columna es el ID del alumno y la segunda el ID del grupo?[S-1/N-0]")
        ans=input()
        if ans.lower()=="s" or ans==str(1):
            texto=""
            arrUsu=[]
            try:
                f = open(self.GroupCreatorCSV,"r",encoding='utf-8')
                texto=f.read()
                f.close()
            except:
                print('ERROR: No se ha encontrado el archivo')
                input("Pulsa INTRO para continuar")
            if texto=="": return
            texto=texto.splitlines()
            for x in texto:
                aux=x.split(";")
                #print (aux)
                try:
                    arrUsu.append( [ aux[0].strip() , aux[1].strip() ] )
                except:
                    print ("Hay un error en el archivo.")
            print ("Archivo cargado, se muestra la primera fila")
            print ("Usuario ID: ",  arrUsu[0][0])
            print ("Grupo ID: ",  arrUsu[0][1])
            print ("¿Es correcta la información? [S-1/N-0]")
            ans=input()
            if ans.lower()=="s" or ans==str(1):
                #print (self.dominio+"circ.php?categ=groups&action=addmember&groupID="+arrUsu[0][1]+"&memberID="+arrUsu[0][0])
                for i in range(len(arrUsu)):
                    numbarritas=20
                    parte=int(numbarritas*i/len(arrUsu))
                    print ("Creando grupos [", "="*parte, " "*(numbarritas-parte-1), "]           ", end="\r")
                    self.s.get(self.dominio+"circ.php?categ=groups&action=addmember&groupID="+arrUsu[i][1]+"&memberID="+arrUsu[i][0])

        else:
            print("Se ha indicado que no existe ese archivo")
            input("Pulsa INTRO para continuar")
            return
        
    def salir(self):
        self.s.close()
        exit()



if __name__=='__main__':
    pass
    #Para debuggear
    #import configparser
    #configFileName='config.ini'
    #config=configparser.ConfigParser()
    #config.read(configFileName)
    #bl=blman (config['DEFAULT']["usu"], config['DEFAULT']["pass"], config['DEFAULT']["dom"], config["DEFAULT"]["cc"])
    #bl.gGetDataFromMatriculaCSV()
    #bl.gGroupCreatorFromNIA()   

    
