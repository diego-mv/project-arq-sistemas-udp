import sqlite3

conn_bd = sqlite3.connect('project-arq-sist.db')
cur = conn_bd.cursor()

cur.execute('CREATE TABLE Rol(id int PRIMARY KEY, nombre varchar(50));')
cur.fetchall()

cur.execute('CREATE TABLE Usuario(rut int PRIMARY KEY, nombre varchar(100), correo varchar(100), fono int, pwhash longtext, rol_id int, FOREIGN KEY(rol_id) REFERENCES Rol(id))')
cur.fetchall()

cur.execute('CREATE TABLE Sala(id int PRIMARY KEY, ubicacion varchar(100), aforo int);')
cur.fetchall()

cur.execute('CREATE TABLE EstadoReserva(id int PRIMARY KEY, nombre varchar(50));')
cur.fetchall()

cur.execute('CREATE TABLE Reserva(id int PRIMARY KEY, inicia varchar(50), termina varchar(50), anfitrion_id int, sala_id int, estado_id int, FOREIGN KEY(anfitrion_id) REFERENCES Usuario(id),FOREIGN KEY(sala_id) REFERENCES Sala(id), FOREIGN KEY(estado_id) REFERENCES EstadoReserva(id))')
cur.fetchall()

cur.execute('CREATE TABLE Invitados(rut int PRIMARY KEY, nombre varchar(100), correo varchar(100), asistio int, reserva_id int, FOREIGN KEY(reserva_id) REFERENCES Reserva(id))')
cur.fetchall()


conn_bd.commit()

