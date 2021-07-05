import sqlite3

conn_bd = sqlite3.connect('project-arq-sist.db')
cur = conn_bd.cursor()

cur.execute('CREATE TABLE Rol(id int PRIMARY KEY AUTOINCREMENT, nombre varchar(50));')

cur.execute('CREATE TABLE Usuario(rut int PRIMARY KEY, nombre varchar(100), correo varchar(100), fono int, pwhash longtext, rol_id int, FOREIGN KEY(rol_id) REFERENCES Rol(id))')

cur.execute('CREATE TABLE Sala(id int PRIMARY KEY AUTOINCREMENT, ubicacion varchar(100), aforo int);')

cur.execute('CREATE TABLE EstadoReserva(id int PRIMARY KEY AUTOINCREMENT, nombre varchar(50));')

cur.execute('CREATE TABLE Reserva(id int PRIMARY KEY AUTOINCREMENT, inicia varchar(50), termina varchar(50), anfitrion_id int, sala_id int, estado_id int, FOREIGN KEY(anfitrion_id) REFERENCES Usuario(id),FOREIGN KEY(sala_id) REFERENCES Sala(id), FOREIGN KEY(estado_id) REFERENCES EstadoReserva(id))')

cur.execute('CREATE TABLE Invitados(rut int PRIMARY KEY, nombre varchar(100), correo varchar(100), asistio int, reserva_id int, FOREIGN KEY(reserva_id) REFERENCES Reserva(id))')

Roles = [(1, "Admin"), (2, "Usuario")]
cur.executemany("INSERT INTO Rol VALUES (?, ?);", Roles)

Salas = [(1, "Piso 1, Sala 12", 10), (2, "Piso 1, Sala 11", 15), (3, "Piso 2, Sala 24", 8)]
cur.executemany("INSERT INTO Rol Sala (?, ?, ?);", Salas)

Estados = [(1, "Reserva realizada"), (2, "Reserva Cancelada"), (2, "Reserva Terminada")]
cur.executemany("INSERT INTO Rol EstadoReserva (?, ?);", Estados)

conn_bd.commit()

