from os import stat
import sys
from datetime import date
import socket
import sqlite3

SERVICE_ADD_PARTICIPANTE_RESERV = 'apr01'
#-------CONNECTION-------#
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER = '200.14.84.235'
PORT = 5000
socket.connect((SERVER, PORT))
print(f'Connected on server: {SERVER} port: {PORT}')

conn_bd = sqlite3.connect('projectArqSist.db')
cur = conn_bd.cursor()
#------------------------#

def generate_transaction_lenght(trans_lenght):
    trans_lenght = str(trans_lenght)
    max_char = 5 #cantidad maxima de caracteres permitida en el bus
    return trans_lenght.rjust(max_char, '0') #string de la transaccion con ceros a la izq para completar largo de 5

trans_cmd = 'sinit' + SERVICE_ADD_PARTICIPANTE_RESERV #registra el servicio en el bus de serv
trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd

socket.send(trans.encode(encoding='UTF-8'))
print(socket.recv(4090).decode('UTF-8'))

while True: 
    print(f"Service '{SERVICE_ADD_PARTICIPANTE_RESERV}' is running and waiting connection")

    try: 
        while True:
            datas_socket = socket.recv(390)
            data_socket_2 = datas_socket[10:]
            data = eval(data_socket_2)
            print(f"Received data: {data}")
            rut_p = data['rut']
            nombre_p = data['nombre']
            correo_p = data['correo']
            reserva_id = data['reserva_id']

            cur.execute(f'INSERT INTO invitados (rut,nombre,correo,asistio,reserva_id) VALUES ({rut_p}, {nombre_p}, {correo_p}, 0, {reserva_id});')
            conn_bd.commit()
            print(f'Invitado agregado en reserva {reserva_id}')

            trans_cmd = SERVICE_ADD_PARTICIPANTE_RESERV + 'Success' 
            trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
            socket.send(trans.encode(encoding='UTF-8'))

    except:
        ex = sys.exc_info()[0]
        print(f"Error: {ex}")
    finally:
        print('Finally')

socket.close()