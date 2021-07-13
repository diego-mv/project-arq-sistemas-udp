import datetime
from getpass import getpass
import socket
import json

#------Servicios---------#
SERVICE_LOGIN = 'log12'
SERVICE_REGISTER = 'rgt12'
SERVICE_LIST_SALAS = 'sls12'
SERVICE_HOR_USADO_SALA = 'hus12'
SERVICE_CONFIRM_RES = 'scr12'
SERVICE_ADD_PARTICIPANTE_RESERV = 'apr12'
SERVICE_RESERV_REALIZADAS = 'rer12'
SERVICE_CANCEL_RESERV = 'car12'
SERVICE_CONFIRM_INV = 'cap12'
SERVICE_NUEVA_SALA = 'nsa12'
SERVICE_DELETE_SALA = 'bsa12'
SERVICE_TRAZABILIDAD = 'tra12'

#-------CONNECTION-------#
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER = '200.14.84.235'
PORT = 5000
socket.connect((SERVER, PORT))
print(f'Connected on server: {SERVER} port: {PORT}')

#------------------------#

def generate_transaction_lenght(trans_lenght):
    trans_lenght = str(trans_lenght)
    max_char = 5 #cantidad maxima de caracteres permitida en el bus
    return trans_lenght.rjust(max_char, '0') #string de la transaccion con ceros a la izq para completar largo de 5

def SendToService(name_service, data):
    dataJson = json.dumps(data, default=str)
    trans_cmd = name_service + dataJson
    trans = generate_transaction_lenght(len(trans_cmd)) + str(trans_cmd)
    socket.send(trans.encode(encoding='UTF-8'))

def GetFromService(name_service): #Verifica si servicio esta UP (?)
    trans_cmd = 'getsv' + name_service
    trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
    socket.send(trans.encode(encoding='UTF-8'))
    status = socket.recv(4090).decode('UTF-8')[10:12]
    return status

rut_usuario = ''
HORARIOS = [
'09:00 - 10:30',
'11:00 - 12:30',
'12:00 - 13:30',
'13:00 - 14:30',
'14:00 - 15:30',
'15:00 - 16:30',
'16:00 - 17:30',
]

print('•• ¡Bienvenido al sistema de reserva de espacios! ••')
while True:
    print('Que desea hacer:')
    print('1. Iniciar Sesión')
    print('2. Registro')
    print('3. Salir')
    opt = int(input("\n>> "))
#-----------------------Iniciar sesion--------------------------#
    if(opt == 1):
        if(GetFromService(SERVICE_LOGIN)) == 'OK':
            print('Ingrese sus credenciales:')
            rut = input('RUT: ')
            psw = password = getpass('Contraseña: ')
            data_login = { 
                'rut': rut,
                'password': psw
            }
            SendToService(SERVICE_LOGIN, data_login)
            
            while True: 
                data_service = socket.recv(390)
                break
            data_service = str(data_service)[14:len(str(data_service))-1]
            if data_service == 'SuccessUSER': #Si el servicio login es exitoso: data_service = b'00000lgn01OKSuccessUSER' Para Rol=Usuario
                rut_usuario = data_login['rut']
                print('Inicio de sesión exitoso.')
                #---------------------------------MENU DESPUES DE LOGGEO-----------------------------------#
                userLogged = True
                while userLogged:
                    print('Qué desea hacer:')
                    print('1. Realizar reserva de sala')
                    print('2. Cancelar reserva')
                    print('3. Salir')
                    opt2 = int(input('>> '))

                    if(opt2 == 1): #realizar reserva
                        if GetFromService(SERVICE_LIST_SALAS) == 'OK':
                            data_list_sala = { 
                                'rut' : rut_usuario
                            }
                            SendToService(SERVICE_LIST_SALAS, data_list_sala)

                            while True: 
                                data_service_salas = socket.recv(390)
                                data_service_salas = json.loads(data_service_salas[12:])
                                break
                            #--------------------------------------MENU SALAS DISPONIBLES----------------------------------#
                            print('Salas disponibles:')
                            for i in range(len(data_service_salas)):
                                print(f'{i+1}. {data_service_salas[i][1]} | Aforo permitido: {data_service_salas[i][2]}')

                            opt_sala = int(input('>> '))
                            fecha_req = input('Ingrese la fecha que requiere una reserva (dd-mm-yyyy): \n>> ') #------------------------!!!!!!!!!!!!!!!!VALIDAR FECHA CON EXPRESION REGULAR dd/mm/yyyy!!!!!!!!!!!!!!!

                            data_sala = {
                                'id_sala': data_service_salas[opt_sala-1][0],
                                'fecha_req': fecha_req    
                            }
                            if GetFromService(SERVICE_HOR_USADO_SALA) == 'OK':
                                SendToService(SERVICE_HOR_USADO_SALA, data_sala)

                                while True: 
                                    data_service_horario_usado = socket.recv(390)
                                    data_service_hor_usado = data_service_horario_usado[12:]
                                    break
                                #-------------------------------------HORARIOS DISPONIBLES DE UNA SALA EN UN DIA ESPECIFICOS-------------------------#
                                HORARIOS_DISP = []
                                print(f'Horarios disponibles en el día {fecha_req}')
                                for i in range(len(HORARIOS)):
                                    if(data_service_horario_usado != HORARIOS[i]):
                                        HORARIOS_DISP.append(HORARIOS[i])
                                        print(f'{i+1}. {HORARIOS[i]}')

                                opt_horario = int(input('>> '))

                                menu_conf_reserva = True
                                PARTICIPANTES = []
                                while menu_conf_reserva: 
                                    #=-------------------------------------------------MENU CONFIRMACION DE RESERVA-----------------------------------------------------#
                                    print('Que desea hacer:')
                                    print('1. Agregar participante a la reunion')
                                    print('2. Confirmar reserva (no puede ingresar más participantes)')
                                    print('3. No realizar reserva y salir')
                                    opt3 = int(input('>> '))

                                    if(opt3 == 1): #Ingresar participante
                                        print('Ingrese datos del participante:')
                                        rut_p = input('RUT: ')
                                        nombre_p = input('Nombre: ')
                                        correo_p = input('Email: ')

                                        if not rut_p or not nombre_p or not correo_p:
                                            print('No se pudo ingresar al participante porque un campo no es correcto.')
                                        else:
                                            PARTICIPANTES.append({
                                                'rut': rut_p,
                                                'nombre': nombre_p,
                                                'correo': correo_p,                                         
                                            })
                                            print('Participante agregado')
                                    elif(opt3 == 2): #Confirmar reserva
                                        if GetFromService(SERVICE_CONFIRM_RES) == 'OK' and GetFromService(SERVICE_ADD_PARTICIPANTE_RESERV) == 'OK':
                                            print('Confirmando reserva...')
                                            data_confirma_reserva = {
                                                'inicia': f'{fecha_req} {HORARIOS_DISP[opt_horario][:5]}',
                                                'termina': f'{fecha_req} {HORARIOS_DISP[opt_horario][8:]}',
                                                'anfitrion_rut': rut_usuario,
                                                'sala_id': data_service_salas[opt_sala-1][0]
                                            }
                                            SendToService(SERVICE_CONFIRM_RES, data_confirma_reserva)

                                            while True: 
                                                data_service_confirm_res = socket.recv(390)
                                                break
                                            #AGREGA A LOS PARTICIPANTES EN LA BD DESPUES DE AGREGAR LA RESERVA EN LA BD
                                            id_nueva_reserva = str(data_service_confirm_res)[21:len(str(data_service_confirm_res))-1]
                                            print('Agregando los participantes a la reserva realizada...')
                                            for i in range(len(PARTICIPANTES)):
                                                data_participante = {
                                                    'rut': PARTICIPANTES[i]['rut'],
                                                    'nombre': PARTICIPANTES[i]['nombre'],
                                                    'correo': PARTICIPANTES[i]['correo'],
                                                    'reserva_id': id_nueva_reserva
                                                }
                                                SendToService(SERVICE_ADD_PARTICIPANTE_RESERV, data_participante)

                                                while True: 
                                                    data_service_horario_usado = socket.recv(390)
                                                    break


                                            print('Reserva realizada, ¡adios!')
                                            menu_conf_reserva = False
                                        else: 
                                            print('Servicio de reserva no disponible')  
                                            menu_conf_reserva = False
                                    else:
                                        print('¡ADIOS!')
                                        menu_conf_reserva = False
                            else: 
                                print('Servicio de reserva no disponible')    
                        else: 
                            print('Servicio de reserva no disponible')

                    elif(opt2 == 2): #Cancela reserva ya guardada en la BD
                        
                        if GetFromService(SERVICE_RESERV_REALIZADAS) == 'OK' and GetFromService(SERVICE_CANCEL_RESERV) == 'OK':
                                data_reservas_realiz = {
                                    'rut': rut_usuario
                                }
                                SendToService(SERVICE_RESERV_REALIZADAS, data_reservas_realiz)

                                while True: 
                                    reservas_realizadas = socket.recv(390)
                                    reservas_realizadas = json.loads(reservas_realizadas[12:])
                                    break
                                print('Indique la reserva que desea cancelar:')
                                for i in range(len(reservas_realizadas)):
                                    print(f'{i+1}. {reservas_realizadas[i]["reserva"]}')
                                opt_reserva_cancel = int(input('>> '))

                                
                                data_cancel_reserva = {
                                    'reserva_id': reservas_realizadas[opt_reserva_cancel-1]['id']
                                }

                                SendToService(SERVICE_CANCEL_RESERV, data_cancel_reserva)
                                while True: 
                                    reservas_realizadas = socket.recv(390)
                                    break
                                print('Reserva cancelada.')
                        else: 
                            print('Servicio no disponible.')
                    elif(opt2 == 3):
                        print('ADIOS!')
                        userLogged = False
                    else:
                        print('Seleccione una opción válida')

            elif data_service == 'SuccessADMIN': #Si el servicio login es exitoso para Rol=Admin
                rut_usuario = data_login['rut']
                adminLogged =True
                while adminLogged:
                    print("Bienvenid@ Admin")
                    print('Que desea hacer:')
                    print('1. Realizar trazabilidad de contactos estrechos')
                    print('2. Crear sala')
                    print('3. Eliminar sala')
                    print('4. Salir')
                    opt_admin = int(input('>> '))

                    if(opt_admin == 1):
                        if GetFromService(SERVICE_TRAZABILIDAD) == 'OK':
                            rut_contagiado = input('Ingrese rut de la persona contagiada\n>> ')
                            data_contagiado = {
                                'rut': rut_contagiado
                            }

                            SendToService(SERVICE_TRAZABILIDAD, data_contagiado)
                            print('Buscando contactos estrechos...')
                            while True: 
                                data_service_contactoEstr = socket.recv(390)
                                data_service_contactoEstr = json.loads(data_service_salas[12:])
                                break
                            if (len(data_service_contactoEstr) == 0):
                                print('La persona no tuvo contactos estrechos.')
                            else:
                                print('Contactos estrechos (rut, nombre, email):')
                                for i in range(len(data_service_contactoEstr)):
                                    print(f'{i+1}) {data_service_contactoEstr[i]["rut"]} - {data_service_contactoEstr[i]["nombre"]} - {data_service_contactoEstr[i]["email"]}')

                                print('----------------------------------------')
                        else:
                            print('Servicio no disponible')
                    elif(opt_admin == 2):
                        if GetFromService(SERVICE_NUEVA_SALA) == 'OK':
                            ubicacion = input('Ingrese la ubicación de la nueva sala\n>> ')
                            aforo = input('Ingrese el aforo máximo de la nueva sala\n>> ')
                            data_nueva_sala = { 
                                'ubicacion' : ubicacion,
                                'aforo' : aforo
                            }
                            SendToService(SERVICE_NUEVA_SALA, data_inv)

                            while True: 
                                data_service_salas = socket.recv(390)
                                break
                            print('Sala creada.')
                        else:
                            print('Servicio no disponible')

                    elif(opt_admin == 3):
                        if GetFromService(SERVICE_LIST_SALAS) == 'OK' and GetFromService(SERVICE_DELETE_SALA) == 'OK':
                            data_list_sala = { 
                                'rut' : rut_usuario
                            }
                            SendToService(SERVICE_LIST_SALAS, data_list_sala)

                            while True: 
                                data_service_salas = socket.recv(390)
                                data_service_salas = json.loads(data_service_salas[12:])
                                break
                            #--------------------------------------MENU SALAS DISPONIBLES----------------------------------#
                            print('Salas disponibles:')
                            for i in range(len(data_service_salas)):
                                print(f'{i+1}. {data_service_salas[i][1]} | Aforo permitido: {data_service_salas[i][2]}')

                            opt_sala_admin = int(input('>> '))
                            
                            data_sala_delete = {
                                'id_sala': data_service_salas[opt_sala-1][0], 
                            }
                            SendToService(SERVICE_DELETE_SALA, data_sala_delete)
                            while True: 
                                data_service_sala = socket.recv(390)
                                break
                            print('Sala eliminada.')

                        else:
                            print('Servicio no disponible')
                    elif(opt_admin == 4):
                        print('¡Adios!')
                        adminLogged = False
                        break
                    else:
                        print('Seleccione una opción válida')

                
            elif data_service == 'SuccessRECEPTION': #Si el servicio login es exitoso para Rol=Admin
                rut_usuario = data_login['rut']
                print('Inicio de sesión exitoso.')
                print("Bienvenid@ Recepción")
                receptionLogged = True
                while receptionLogged:
                    print('1. Confirmar asistencia de invitados.')
                    print('2. Cancelar reunión.')
                    print('3. Salir')
                    opt_rec = int(input('>> '))

                    if(opt_rec == 1): #CONFIRMAR ASISTENCIA INVITADO
                        rut = input('Ingrese el rut del invitado\n>> ')
                        reserva_id = input('Ingrese el codigo de la reserva\n>> ')

                        if GetFromService(SERVICE_CONFIRM_INV) == 'OK':
                            data_inv = { 
                                'rut' : rut,
                                'reserva_id' : reserva_id
                            }
                            SendToService(SERVICE_LIST_SALAS, data_inv)

                            while True: 
                                data_service_salas = socket.recv(390)
                                data_service_salas = json.loads(data_service_salas[12:])
                                break
                            
                            print(f'El invitado {rut} ha sido ingresado con éxito.')
                        else:
                            print('Servicio no disponible.')
                    elif(opt_rec == 2): #CANCELAR RESERVA
                        rut = input('Ingrese el rut del anfitrión\n>> ')

                        if GetFromService(SERVICE_RESERV_REALIZADAS) == 'OK' and GetFromService(SERVICE_CANCEL_RESERV) == 'OK':
                            SendToService(SERVICE_RESERV_REALIZADAS, data_reservas_realiz)
                            while True: 
                                reservas_realizadas = socket.recv(390)
                                break
                            
                            for i in range(len(reservas_realizadas)):
                                print(f'{i+1}. {reservas_realizadas[i][1]}')
                            opt_reserva_cancel_rec = int(input('>> '))

                            for i in range(len(reservas_realizadas)):
                                if reservas_realizadas[opt_reserva_cancel_rec-1]==reservas_realizadas[i]:
                                    reserva_id_toCancel = reservas_realizadas[i][0]
                            data_cancel_reserva = {
                                'reserva_id': reserva_id_toCancel
                            }

                            SendToService(SERVICE_CANCEL_RESERV, data_cancel_reserva)
                            while True: 
                                reservas_realizadas = socket.recv(390)
                                break
                            print('Reserva cancelada.')
                        else:
                            print('Servicio no disponible.')
                    elif(opt_rec == 3):
                        print('ADIOS!')
                        receptionLogged=False
                    else:
                        print('Seleccione una opción válida')
            else:
                print('No se pudo iniciar sesión, intente nuevamente.')
                pass
#--------------------------Registro--------------------------#
    elif(opt == 2):
        if(GetFromService(SERVICE_REGISTER)) == 'OK':
            print('Ingrese los datos para su cuenta:')
            rut = input('RUT: ')
            name = input('Nombre: ')
            email = input('Email: ')
            fono = input('Teléfono: ')
            psw = password = getpass('Contraseña: ')

            data = {
                'rut': rut,
                'nombre': name,
                'correo': email,
                'fono': fono,
                'password': psw
            }
            SendToService(SERVICE_REGISTER, data)
            
            while True: 
                data_service = socket.recv(390)
                break
            print('Registro exitoso, inicie sesion')
            #if register is success else register is error ......
#----------------------------Salir----------------------------#
    elif(opt == 3):
        print('¡Hasta luego!') 
        break
    else:
        print('¡UPS! Seleccione una opción válida.')
