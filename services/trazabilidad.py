from os import stat
import sys
import json
from datetime import date
import socket
import sqlite3
import datetime

SERVICE_TRAZABILIDAD = 'tra01'
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

trans_cmd = 'sinit' + SERVICE_TRAZABILIDAD #registra el servicio en el bus de serv
trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd

socket.send(trans.encode(encoding='UTF-8'))
print(socket.recv(4090).decode('UTF-8'))

while True: 
    print(f"Service '{SERVICE_TRAZABILIDAD}' is running and waiting connection")
    try: 
        while True:
            datas_socket = socket.recv(390)
            data_socket_2 = datas_socket[10:]
            data = eval(data_socket_2)
            print(f"Received data: {data}")
            rut_contagiado = data['rut']

            #dd-mm-yyyy HH:mm
            dias_atras = datetime.datetime.now() + datetime.timedelta(days=-15)
            dia = str(dias_atras.day).rjust(2, '0')
            mes = str(dias_atras.month).rjust(2, '0')
            anio = str(dias_atras.year).rjust(2, '0')
            contactos_estrechos = []
            invitados = []

            cur.execute(f'SELECT reserva_id FROM invitados WHERE rut=? AND asistio=1',(rut_contagiado))
            res = cur.fetchall()
            id_reservas_contagiado = []
            for i in range(len(res)):
                id_reservas_contagiado.append(res[i][0])
            
            cur.execute(f'SELECT * FROM reserva  WHERE id IN {tuple(id_reservas_contagiado)} AND ((CAST(SUBSTR(inicia,4,5) AS INTEGER)>=? AND CAST(SUBSTR(inicia,1,2) AS INTEGER)<=?) OR (CAST(SUBSTR(inicia,4,5) AS INTEGER)=? AND CAST(SUBSTR(inicia,1,2) AS INTEGER)>=?))',(mes,dia,mes,dia))
            reservas_recientes = cur.fetchall()
            
            for i in range(len(reservas_recientes)):
                cur.execute(f'SELECT * FROM usuario WHERE rut=?;',(reservas_recientes[i][3]))
                user = cur.fetchall()
                contactos_estrechos.append({
                    'rut': user[0][0], 
                    'nombre': user[0][1],
                    'email': user[0][2],
                })
                cur.execute(f'SELECT * FROM invitados WHERE reserva_id=?;',(reservas_recientes[i][0]))
                invitados += cur.fetchall()
            
            for i in range(len(invitados)):
                contactos_estrechos.append({
                    'rut': invitados[i][0], 
                    'nombre': invitados[i][1],
                    'email': invitados[i][2],
                })
            jsonSalas = json.dumps(contactos_estrechos)

            trans_cmd = SERVICE_TRAZABILIDAD + jsonSalas
            trans = generate_transaction_lenght(len(trans_cmd)) + trans_cmd
            socket.send(trans.encode(encoding='UTF-8'))
    except:
        ex = sys.exc_info()[0]
        print(f"Error: {ex}")
    finally:
        print('Finally')

socket.close()
