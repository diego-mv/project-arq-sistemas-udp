from os import stat
import traceback
from datetime import date
import sys
import socket
import sqlite3

SERVICE_LOGIN = 'log03'
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

trans_cmd = 'sinit' + SERVICE_LOGIN #registra el servicio en el bus de serv
trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd

socket.send(trans.encode(encoding='UTF-8'))
print(socket.recv(4090).decode('UTF-8'))

while True: 
    print(f"Service '{SERVICE_LOGIN}' is running and waiting connection")

    try: 
        while True:
            datas_socket = socket.recv(390)
            data_socket_2 = datas_socket[10:]
            data = eval(data_socket_2)
            print(f"Received data: {data}")
            rut = data['rut']
            password_hash = data['password']
            
            cur.execute(f'SELECT * FROM usuario WHERE rut=?',(rut,))
            result_rut = cur.fetchall()

            if(len(result_rut)==0):
                print('User not found')
                trans_cmd = SERVICE_LOGIN + 'Error'
                trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
                socket.send(trans.encode(encoding='UTF-8'))
            else:
                if(password_hash == result_rut[0][4]):
                    if(result_rut[0][5] == 1):
                        print('Login success')
                        trans_cmd = SERVICE_LOGIN + 'SuccessADMIN' 
                        trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
                        socket.send(trans.encode(encoding='UTF-8'))
                    elif(result_rut[0][5] == 2):
                        print('Login success')
                        trans_cmd = SERVICE_LOGIN + 'SuccessUSER' 
                        trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
                        socket.send(trans.encode(encoding='UTF-8'))
                    elif(result_rut[0][5] == 3):
                        print('Login success')
                        trans_cmd = SERVICE_LOGIN + 'SuccessRECEPTION' 
                        trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
                        socket.send(trans.encode(encoding='UTF-8'))
                    else:
                        print('Login failed')
                        trans_cmd = SERVICE_LOGIN + 'Error'
                        trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
                        socket.send(trans.encode(encoding='UTF-8'))
                else:
                    print('Login failed')
                    trans_cmd = SERVICE_LOGIN + 'Error'
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
