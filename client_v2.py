import datetime
from getpass import getpass
import socket
import json
from typing import Text

#------Servicios---------#
SERVICE_LOGIN = 'log24'
SERVICE_REGISTER = 'rgt24'
SERVICE_LIST_SALAS = 'sls24'
SERVICE_HOR_USADO_SALA = 'hus24'
SERVICE_CONFIRM_RES = 'scr24'
SERVICE_ADD_PARTICIPANTE_RESERV = 'apr24'
SERVICE_RESERV_REALIZADAS = 'rer24'
SERVICE_CANCEL_RESERV = 'car24'
SERVICE_CONFIRM_INV = 'cap24'
SERVICE_NUEVA_SALA = 'nsa24'
SERVICE_DELETE_SALA = 'bsa24'
SERVICE_TRAZABILIDAD = 'tra24'

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
    if opt == 1:
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
                data_sv_login = socket.recv(390)
                break
            login_response = str(data_sv_login)[14:len(str(data_sv_login))-1]

            if login_response == 'SuccessUSER':
                rut_current_user = rut
                print('')
            elif login_response == 'SuccessADMIN':
                rut_current_user = rut
                print('')
            elif login_response == 'SuccessRECEPTION':
                rut_current_user = rut
                print("Bienvenid@ Recepción")
                receptionLogged = True

                while receptionLogged:
                    print('1. Confirmar asistencia de invitados.')
                    print('2. Cancelar reunión.')
                    print('3. Salir')
                    opt_rec = int(input('>> '))
                    
                    if(opt_rec == 1): #CONFIRMAR ASISTENCIA INVITADO
                        rut_inv = input('Ingrese el rut del invitado\n>> ')
                        reserva_id = input('Ingrese el codigo de la reserva\n>> ')

                        if GetFromService(SERVICE_CONFIRM_INV) == 'OK':
                            data_inv = { 
                                'rut' : rut_inv,
                                'reserva_id' : reserva_id
                            }
                            SendToService(SERVICE_LIST_SALAS, data_inv)

                            while True: 
                                data_conf_inv = socket.recv(390)
                                data_conf_inv = json.loads(data_conf_inv[12:])
                                break
                            conf_inv_resp = str(data_conf_inv)[14:len(str(data_conf_inv))-1]

                            if conf_inv_resp == "":
                                print("Ha ocurrido un error confirmando la asistencia, intente nuevamente")
                            else:
                                print(f'El invitado {rut_inv} ha sido ingresado con éxito.')
                        else:
                            print('Servicio no disponible.')
                    
                    elif(opt_rec == 2): #CANCELAR RESERVA
                        rut_canc_reserv = input('Ingrese el rut del anfitrión\n>> ')
                        data_res_realiz_recep = {
                            'rut': rut_canc_reserv
                        }
                        if GetFromService(SERVICE_RESERV_REALIZADAS) == 'OK' and GetFromService(SERVICE_CANCEL_RESERV) == 'OK':
                            SendToService(SERVICE_RESERV_REALIZADAS, rut_canc_reserv)
                            while True: 
                                reservas_realizadas_recep = socket.recv(390)
                                break
                            responde_res_real_recep = str(reservas_realizadas_recep)[14:len(str(reservas_realizadas_recep))-1]
                            if responde_res_real_recep != "Error":
                                for i in range(len(reservas_realizadas_recep)):
                                    print(f'{i+1}. {reservas_realizadas_recep[i][1]}')
                                opt_reserva_cancel_rec = int(input('>> '))

                                for i in range(len(reservas_realizadas_recep)):
                                    if reservas_realizadas_recep[opt_reserva_cancel_rec-1]==reservas_realizadas_recep[i]:
                                        reserva_id_toCancel = reservas_realizadas_recep[i][0]
                                data_cancel_reserva = {
                                    'reserva_id': reserva_id_toCancel
                                }

                                SendToService(SERVICE_CANCEL_RESERV, data_cancel_reserva)
                                while True: 
                                    reserva_cancelada_sv = socket.recv(390)
                                    break
                                print('Reserva cancelada.')
                            else:
                                 print("Ha ocurrido un error cancelando la reserva, intente nuevamente")
                        else:
                            print('Servicio no disponible.')
                    elif(opt_rec == 3):
                        print('ADIOS!')
                        receptionLogged=False
                    else:
                        print('Seleccione una opción válida')

            else:
                print('Ha ocurrido un error.')


    elif opt == 2:
        print('register')
    elif opt == 3:
        print('Adios!')
        break
    else:
        print('Elija una opción válida.')
