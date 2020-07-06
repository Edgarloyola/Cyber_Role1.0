from os import listdir
from os.path import isfile, join
import records
import json

db = records.Database(
    'postgresql://localhost/cyber_role?user=admin&password=admin1234')


# rows = db.query('select * from users')
# rows = db.query('select * from roles')
# rows = db.query('select * from lo_users')
# rows = db.query('select * from courses')
# rows = db.query('select * from los')
# rows = db.query('select * from categories')
# rows = db.query('select * from specialists')
# rows = db.query('select * from work_roles')
# rows = db.query('select * from ksats')
# rowsK = db.query('select * from knowledges')
# rowsS = db.query('select * from skills')
# rowsA = db.query('select * from abilities')
# rowsT = db.query('select * from tasks')
# db.query('insert into table_name (column1,column2,...)
# VALUES('value1','value2'),(4,5,6),(7,8,9)')
# print("----------------")
# for r in rows:
#     if r.id > 46 and r.id < 54:
#         print(r.id)
#         print("-----------El nombre del WorkRole es----------")
#         print(r.name)
#         print("-----------El nombre del WorkRole es----------")
#         print(r.ksat_ids)
# print("----------------")

# print("+++++++++++++++++++++")
# for r in rows:
#     print(r)
#     for lo in r.los:
#         print(lo.time)
#         print(lo.cost)
#         print(lo.reputation)
#     print("---un learning object----")

# print("+++++++++++++++++++++")

# Este script nos permite actualizar la db con los KSA de los work roles que hemos obtenido en ficheros JSON
mi_path = "WorkRole-JSON"
file_jsons = [
    cosa for cosa in listdir(mi_path)
    if isfile(join(mi_path, cosa))]

#Recorremos cada fichero JSON para que pueda ser insertada su info de KSA's
for archivo in file_jsons:
    # print(archivo)
    # Ejemplo de como leer un fichero JSON
    file_json = f'{"WorkRole-JSON/"}{archivo}'
    with open(file_json) as file:
        # Obtenemos el json del fichero
        data = json.load(file)

        count = 0
        listaKnowledges = []

        res = list(data.keys())[0]
        #Obtenemos el nombre del work role
        firstkey = str(res)

        for i in data[firstkey]["knowledges_ids"]:
            l = list(data[firstkey]["knowledges_ids"][count].values())
            value = l[0]
            listaKnowledges.append(value)
            count += 1

        count = 0
        listaSkills = []

        for i in data[firstkey]["skills_ids"]:
            l = list(data[firstkey]["skills_ids"][count].values())
            value = l[0]
            listaSkills.append(value)
            count += 1

        count = 0
        listaAbilities = []

        for i in data[firstkey]["abilities_ids"]:
            l = list(data[firstkey]["abilities_ids"][count].values())
            value = l[0]
            listaAbilities.append(value)
            count += 1

        count = 0
        listaTasks = []

        for i in data[firstkey]["tasks_ids"]:
            l = list(data[firstkey]["tasks_ids"][count].values())
            value = l[0]
            listaTasks.append(value)
            count += 1

        #print("**************+YA TENGO LAS DESCRIP DE LOS KnowledgeSS***************")

        dictK = {}
        K = "myK000"
        for i in listaKnowledges:
            existe = db.query(
                'select * from knowledges where description=:descrip', descrip=i)
            # #print(db.query('select * from knowledges where description=:descrip', descrip=i))
            # #print(existe.first())
            elem = existe.first()
            if elem:
                #print("existe en la db esa description")
                # print(elem.id)
                # print(elem.description)
                if (elem.id < 10):
                    k = f'{K}{elem.id}'
                    dictK[k] = elem.description
                elif (elem.id < 100):
                    k = f'{"myK00"}{elem.id}'
                    dictK[k] = elem.description
                else:
                    k = f'{"myK0"}{elem.id}'
                    dictK[k] = elem.description

        # #print(dictK)

        data[firstkey]["knowledges_ids"] = dictK
        #print("**************+YA TENGO LAS DESCRIP DE LOS KnowledgeSS***************")

        dictS = {}
        S = "myS000"
        #print("**************+YA TENGO LAS DESCRIP DE LOS skills***************")
        for i in listaSkills:
            # #print(i)
            existe = db.query(
                'select * from skills where description=:descrip', descrip=i)
            # #print(db.query('select * from skills where description=:descrip', descrip=i))
            # #print(existe.first())
            elem = existe.first()
            if elem:
                # #print("existe en la db esa description")
                # #print(elem.id)
                # #print(elem.description)
                if (elem.id < 10):
                    s = f'{S}{elem.id}'
                    dictS[s] = elem.description
                elif (elem.id < 100):
                    s = f'{"myS00"}{elem.id}'
                    dictS[s] = elem.description
                else:
                    s = f'{"myS0"}{elem.id}'
                    dictS[s] = elem.description

        # #print(dictS)
        # Seteamos el dictionario original
        data[firstkey]["skills_ids"] = dictS

        #print("**************+YA TENGO LAS DESCRIP DE LOS skills***************")

        dictA = {}
        A = "myA000"
        #print("**************+YA TENGO LAS DESCRIP DE LOS Abilities***************")
        for i in listaAbilities:
            # #print(i)
            existe = db.query(
                'select * from abilities where description=:descrip', descrip=i)
            # #print(db.query('select * from knowledges where description=:descrip', descrip=i))
            # #print(existe.first())
            elem = existe.first()
            if elem:
                # #print("existe en la db esa description")
                # #print(elem.id)
                # #print(elem.description)
                if (elem.id < 10):
                    a = f'{A}{elem.id}'
                    dictA[a] = elem.description
                elif (elem.id < 100):
                    a = f'{"myA00"}{elem.id}'
                    dictA[a] = elem.description
                else:
                    a = f'{"myA0"}{elem.id}'
                    dictA[a] = elem.description

        # #print(dictA)
        data[firstkey]["abilities_ids"] = dictA

        #print("**************+YA TENGO LAS DESCRIP DE LOS Abilities***************")

        dictT = {}
        T = "myT000"
        #print("**************+YA TENGO LAS DESCRIP DE LOS tasks***************")
        for i in listaTasks:
            # #print(i)
            existe = db.query(
                'select * from tasks where description=:descrip', descrip=i)
            # #print(db.query('select * from knowledges where description=:descrip', descrip=i))
            # #print(existe.first())
            elem = existe.first()
            if elem:
                # #print("existe en la db esa description")
                # #print(elem.id)
                # #print(elem.description)
                if (elem.id < 10):
                    t = f'{T}{elem.id}'
                    dictT[t] = elem.description
                elif (elem.id < 100):
                    t = f'{"myT00"}{elem.id}'
                    dictT[t] = elem.description
                elif (elem.id < 1000):
                    t = f'{"myT0"}{elem.id}'
                    dictT[t] = elem.description
                else:
                    t = f'{"myT"}{elem.id}'
                    dictT[t] = elem.description

        # #print(dictT)

        data[firstkey]["tasks_ids"] = dictT
        #print("**************+YA TENGO LAS DESCRIP DE LOS tasks***************")

        #print("++++++++++++++++++++DICTIONARIO SETEADO Y CONGRUENTE CON NUESTRA DB+++++++++++++++\n")

        # #print(data)

        # query = f'{"update work_roles set ksat_ids = "} str(data) {" where name = "}{str(firstkey)}'
        # db.query(query)
        print("************La primera clave es***********")
        print(firstkey)
        # print(str(firstkey))
        # if "Cyber Workforce Developer and Manager" in data:
        #     print(data["Cyber Workforce Developer and Manager"])
        # if "Cyber Workforce Developer and Manager" == str(firstkey):
        #     print("Entro por aquiii")
        #     print(data)
        print("************La primera clave es************\n")
        update = db.query('update work_roles set ksat_ids = :values_ksa where name=:name',
                          values_ksa=json.dumps(data), name=firstkey)

        count += 1
        # print(update)
        # if update:
        #     # print(update)
        #     #print("Actualizado correctamente")
        #     count += 1

        print("Actualizaciones correctas:  ")
        print(count)
        # escribir en los ficheros JSON
        # with open(file_json, 'w') as file_w:
        #     json.dump(data, file_w, indent=4)
        #print("++++++++++++++++++++DICTIONARIO SETEADO Y CONGRUENTE CON NUESTRA DB+++++++++++++++++++")

        # #print(stra == strb)

        # db.query("DELETE FROM users")
        # db.query("TRUNCATE TABLE users")

        # Sentencia query para update

        # UPDATE table_name
        # SET column1 = value1, column2 = value2, ...
        # WHERE condition;

