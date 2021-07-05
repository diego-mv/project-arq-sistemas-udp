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

def GetFromService(name_service):
    trans_cmd = 'getsv' + name_service
    trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
    socket.send(trans.encode(encoding='UTF-8'))
    status = socket.recv(4090).decode('UTF-8')
    print(status)
    return status

print('•• ¡Bienvenido al sistema de reserva de espacios! ••')
while True:
    print('1. Iniciar Sesión')
    print('2. Registro')
    print('3. Salir')
    opt = int(input("\n>> "))
    
    if(opt == 1):
        if(GetFromService('login-sist-reserva')):
            print('Ingrese sus credenciales:')
            rut = input('RUT: ')
            psw = password = getpass('Contraseña: ')
            data = { 
                'rut': rut,
                'password': psw
            }
            SendToService('login-sist-reserva', data)
            
            while True: 
                data_service = socket.recv(390)
                print(data_service)
                break
            print(data_service)
#--------------------------Registro--------------------------#
    elif(opt == 2):
        if(GetFromService('registro-sist-reserva')):
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
            SendToService('registro-sist-reserva', data)
            
            while True: 
                data_service = socket.recv(390)
                print(data_service)
                break
            print(data_service)

    elif(opt == 3):
        print('¡Hasta luego!') 
        break
    else:
        print('¡UPS! Seleccione una opción válida.')
