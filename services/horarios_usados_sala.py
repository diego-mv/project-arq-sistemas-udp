import json
from os import stat
import sys
from datetime import date
import socket
import traceback
import sqlite3

SERVICE_HOR_USADO_SALA = 'hus11'
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

trans_cmd = 'sinit' + SERVICE_HOR_USADO_SALA #registra el servicio en el bus de serv
trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd

socket.send(trans.encode(encoding='UTF-8'))
print(socket.recv(4090).decode('UTF-8'))

while True: 
    print(f"Service '{SERVICE_HOR_USADO_SALA}' is running and waiting connection")

    try: 
        while True:
            data_socket = socket.recv(390)
            data_socket_2 = data_socket[10:]
            data = eval(data_socket_2)
            print(f"Received data: {data}")
            id_sala = data['id_sala']
            fecha_req = data['fecha_req']

            cur.execute(f'SELECT * FROM reserva WHERE sala_id=? AND SUBSTR(inicia,1,10)=?;',(id_sala, fecha_req,))
            result_salas = cur.fetchall()
            horarios_usados = []
            for i in range(len(result_salas)):
                horarios_usados.append(f'{result_salas[i][1][0:11]} - {result_salas[i][2][0:11]}')

            jsonHorariosUsados = json.dumps(horarios_usados)
            trans_cmd = SERVICE_HOR_USADO_SALA + jsonHorariosUsados
            trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
            socket.send(trans.encode(encoding='UTF-8'))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))       
    except:
        ex = traceback.print_exc()
        print(f"Error: {ex}")
    finally:
        print('Finally')

socket.close()
