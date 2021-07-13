from os import stat
import sys
from datetime import date
import socket
import traceback
import sqlite3
import json

SERVICE_RESERV_REALIZADAS = 'rer13'
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

trans_cmd = 'sinit' + SERVICE_RESERV_REALIZADAS #registra el servicio en el bus de serv
trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd

socket.send(trans.encode(encoding='UTF-8'))
print(socket.recv(4090).decode('UTF-8'))

while True: 
    print(f"Service '{SERVICE_RESERV_REALIZADAS}' is running and waiting connection")

    try: 
        while True:
            datas_socket = socket.recv(390)
            data_socket_2 = datas_socket[10:]
            data = eval(data_socket_2)
            print(f"Received data: {data}")
            rut = data['rut']

            cur.execute(f'SELECT * FROM reserva WHERE anfitrion_id=? AND estado_id=1;',(rut,))
            result = cur.fetchall()
            conn_bd.commit()
            result_reservas = []

            for i in range(len(result)):
                cur.execute(f'SELECT ubicacion FROM sala WHERE id=?;',(result[i][4],))
                result_sala = cur.fetchall()
                result_reservas.append(
                    {
                        'id' : result[i][0],
                        'reserva': f"{result_sala[i][0]} {result[i][1]} - {result[i][2][11:]}"
                    }
                )
            
            jsonSalas = json.dumps(result_reservas)
            trans_cmd = SERVICE_RESERV_REALIZADAS + jsonSalas
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
