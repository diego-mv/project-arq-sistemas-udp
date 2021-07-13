from os import stat
from datetime import date
import sys
import socket
import traceback
import sqlite3

SERVICE_REGISTER = 'rgt02'
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

trans_cmd = 'sinit' + SERVICE_REGISTER #registra el servicio en el bus de serv
trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd

socket.send(trans.encode(encoding='UTF-8'))
print(socket.recv(4090).decode('UTF-8'))

while True: 
    print(f"Service '{SERVICE_REGISTER}' is running and waiting connection")

    try: 
        while True:
            datas_socket = socket.recv(390)
            data_socket_2 = datas_socket[10:]
            data = eval(data_socket_2)
            print(f"Received data: {data}")
            rut = data['rut']

            cur.execute(f'SELECT rut FROM usuario WHERE rut=?', (rut,))
            result_rut = cur.fetchall()

            if(len(result_rut) == 0):
                password_hash = data['password']
                nombre = data['nombre']
                correo = data['correo']
                fono = data['fono']

                cur.execute(f'INSERT INTO usuario (rut, nombre, correo, fono, pwhash, rol_id) VALUES (?,?,?,?,?,2);',(rut,nombre,correo,fono,password_hash,))
              
                conn_bd.commit()

                print('User saved, sending data to client')
                trans_cmd = SERVICE_REGISTER + 'Success' 
                trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
                socket.send(trans.encode(encoding='UTF-8'))
            else:
                print('User already exist')
                trans_cmd = SERVICE_REGISTER + 'Error'
                trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
                socket.send(trans.encode(encoding='UTF-8'))
            break
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
    except:
        ex = traceback.print_exc()
        print(f"Error: {ex}")
    finally:
        print('Finally')

socket.close()
