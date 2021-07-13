import sqlite3

conn_bd = sqlite3.connect('projectArqSist.db')
cur = conn_bd.cursor()

cur.execute('SELECT * FROM invitados;')
invitados = cur.fetchall()
print(f'Invitados:\n{invitados}')

cur.execute('SELECT * FROM usuario;')
usuario = cur.fetchall()
print(f'Usuarios:\n{usuario}')

cur.execute('SELECT * FROM reserva;')
reserva = cur.fetchall()
print(f'Reserva:\n{reserva}')

cur.execute('SELECT * FROM sala;')
salas = cur.fetchall()
print(f'Salas:\n{salas}')
