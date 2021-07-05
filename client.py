from getpass import getpass
import asyncio
import socket
import json

#-------CONNECTION-------#
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER = '200.14.84.235'
PORT = 5000
socket.connect((SERVER, PORT))
print(f'Connected on server: {SERVER} port: {PORT}')

#------------------------#

def generate_transaction_lenght(trans_lenght):
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
    print(status)
    return status

rut_usuario = ''
HORARIOS = [
'09:00 - 10:00',
'10:00 - 11:00',
'11:00 - 12:00',
'12:00 - 13:00',
'13:00 - 14:00',
'14:00 - 15:00',
'15:00 - 16:00',
'16:00 - 17:00'
]

print('•• ¡Bienvenido al sistema de reserva de espacios! ••')
while True:
    print('Que desea hacer:')
    print('1. Iniciar Sesión')
    print('2. Registro')
    print('3. Salir')
    opt = int(input("\n>> "))
    
    if(opt == 1):
        if(GetFromService('login_sist_reserva')) == 'OK':
            print('Ingrese sus credenciales:')
            rut = input('RUT: ')
            psw = password = getpass('Contraseña: ')
            data_login = { 
                'rut': rut,
                'password': psw
            }
            SendToService('login_sist_reserva', data_login)
            
            while True: 
                data_service = socket.recv(390)
                break

            if (True): #falta condicion de logged true IF LOGGIN == TRUE
                rut_usuario = data_login['rut']
                print('Inicio de sesión exitoso.')
                #---------------------------------MENU DESPUES DE LOGGEO-----------------------------------#
                print('Qué desea hacer:')
                print('1. Realizar reserva de sala')
                print('2. Cancelar reserva')
                print('3. Salir')
                opt2 = int(input('>> '))

                if(opt2 == 1): #realizar reserva
                    if GetFromService('lista_de_salas') == 'OK':
                        data_list_sala = { 
                            'rut' : rut_usuario
                        }
                        SendToService('lista_de_salas', data_list_sala)
                        
                        while True: 
                            data_service_salas = socket.recv(390)
                            break
                        #--------------------------------------MENU SALAS DISPONIBLES----------------------------------#
                        print('Salas disponibles:')
                        for i in len(data_service_salas):
                            print(f'{i+1}. {data_service_salas[1]} | Aforo permitido: {data_service_salas[2]}')
                        
                        opt_sala = int(input('>> '))
                        fecha_req = input('Ingrese la fecha que requiere una reserva (dd-mm-yyyy): \n>> ') #------------------------!!!!!!!!!!!!!!!!VALIDAR FECHA CON EXPRESION REGULAR dd/mm/yyyy!!!!!!!!!!!!!!!

                        data_sala = {
                            'id_sala': data_service_salas[opt_sala-1][0],
                            'fecha_req': fecha_req    
                        }
                        if GetFromService('horarios_usados_sala') == 'OK':
                            SendToService('horarios_usados_sala', data_sala)

                            while True: 
                                data_service_horario_usado = socket.recv(390)
                                break
                            #-------------------------------------HORARIOS DISPONIBLES DE UNA SALA EN UN DIA ESPECIFICOS-------------------------#
                            HORARIOS_DISP = []
                            print(f'Horarios disponibles en el día {fecha_req}')
                            for i in len(HORARIOS):
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
                                            'reserva_id': data_service_salas[opt_sala-1][0]
                                        })
                                        print('Participante agregado')
                                elif(opt3 == 2): #Confirmar reserva
                                    if GetFromService('confirmar_reserva') == 'OK' and GetFromService('agregar_participante_en_reserva') == 'OK':
                                        print('Confirmando reserva...')
                                        data_confirma_reserva = {
                                            'inicia': f'{fecha_req} {HORARIOS_DISP[opt_horario][:5]}',
                                            'termina': f'{fecha_req} {HORARIOS_DISP[opt_horario][8:]}',
                                            'anfitrion_rut': rut_usuario,
                                            'sala_id': data_service_salas[opt_sala-1][0]
                                        }
                                        SendToService('confirmar_reserva', data_confirma_reserva)

                                        while True: 
                                            data_service_horario_usado = socket.recv(390)
                                            print(data_service)
                                            break
                                        #AGREGA A LOS PARTICIPANTES EN LA BD DESPUES DE AGREGAR LA RESERVA EN LA BD
                                        data_participante = {
                                            'rut': rut_p,
                                            'nombre': nombre_p,
                                            'correo': correo_p,
                                            'reserva_id': data_service_salas[opt_sala-1][0]
                                        }
                                        SendToService('agregar_participante_en_reserva', data_participante)

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
                    print('Indique la reserva que desea cancelar:')
                    if GetFromService('reservas_realizadas') == 'OK' and GetFromService('cancelar_reserva') == 'OK':
                            data_reservas_realiz = {
                                'rut_anfitrion': rut_usuario
                            }
                            SendToService('reservas_realizadas', data_reservas_realiz)
                            
                            while True: 
                                reservas_realizadas = socket.recv(390)
                                break
                            
                            for i in len(reservas_realizadas):
                                print(f'{i+1}. {reservas_realizadas[i][1]}')
                            opt_reserva_cancel = int(input('>> '))
                            data_cancel_reserva = {
                                'reserva_id': reservas_realizadas[opt_reserva_cancel-1][0]
                            }
                            SendToService('cancelar_reserva', data_cancel_reserva)
                            while True: 
                                reservas_realizadas = socket.recv(390)
                                break
                            print('Reserva cancelada.')
                else:
                    print('¡ADIOS!')
                    pass

            else:
                print('No se pudo iniciar sesión, intente nuevamente.')
                pass
#--------------------------Registro--------------------------#
    elif(opt == 2):
        if(GetFromService('registro_sist_reserva')) == 'OK':
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
            SendToService('registro_sist_reserva', data)
            
            while True: 
                data_service = socket.recv(390)
                print(data_service)
                break
            print(data_service)

            #if register is success else register is error ......

    elif(opt == 3):
        print('¡Hasta luego!') 
        break
    else:
        print('¡UPS! Seleccione una opción válida.')
