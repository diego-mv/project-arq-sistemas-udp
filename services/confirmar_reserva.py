from os import stat
import sys
from datetime import date
import socket
import sqlite3

SERVICE_CONFIRM_RES = 'scr01'
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

trans_cmd = 'sinit' + SERVICE_CONFIRM_RES #registra el servicio en el bus de serv
trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd

socket.send(trans.encode(encoding='UTF-8'))
print(socket.recv(4090).decode('UTF-8'))

while True: 
    print(f"Service '{SERVICE_CONFIRM_RES}' is running and waiting connection")
    try: 
        while True:
            datas_socket = socket.recv(390)
            data_socket_2 = datas_socket[10:]
            data = eval(data_socket_2)
            print(f"Received data: {data}")
            inicia = data['inicia']
            termina = data['termina']
            anfitrion_id = data['anfitrion_rut']
            sala_id = data['sala_id']
            horario = data['horario']
    	    #estado 1: Reserva realizada
            cur.execute(f'INSERT INTO reserva (inicia,termina,anfitrion_id, sala_id, estado_id) VALUES ({inicia}, {termina}, {anfitrion_id}, {sala_id}, 1);')
            conn_bd.commit()
            print('Reserva realizada')

            trans_cmd = SERVICE_CONFIRM_RES + 'Success' 
            trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
            socket.send(trans.encode(encoding='UTF-8'))
    except:
        ex = sys.exc_info()[0]
        print(f"Error: {ex}")
    finally:
        print('Finally')

socket.close()