rut_usuario = data_login['rut']
                print('Inicio de sesión exitoso.')
                #---------------------------------MENU DESPUES DE LOGGEO-----------------------------------#
                print('Qué desea hacer:')
                print('1. Realizar reserva de sala')
                print('2. Cancelar reserva')
                print('3. Salir')
                opt2 = int(input('>> '))

                if(opt2 == 1): #realizar reserva
                    if GetFromService(SERVICE_LIST_SALAS) == 'OK':
                        data_list_sala = { 
                            'rut' : rut_usuario
                        }
                        SendToService(SERVICE_LIST_SALAS, data_list_sala)
                        
                        while True: 
                            data_service_salas = socket.recv(390)
                            data_service_salas = json.loads(data_service_salas[12:])
                            break
                        #--------------------------------------MENU SALAS DISPONIBLES----------------------------------#
                        print('Salas disponibles:')
                        for i in len(data_service_salas):
                            print(f'{i+1}. {data_service_salas[1]} | Aforo permitido: {data_service_salas[2]}')
                        
                        opt_sala = int(input('>> '))
                        fecha_req = input('Ingrese la fecha que requiere una reserva (dd-mm-yyyy): \n>> ') #------------------------!!!!!!!!!!!!!!!!VALIDAR FECHA CON EXPRESION REGULAR dd/mm/yyyy!!!!!!!!!!!!!!!

                        data_sala = {
                            'id_sala': data_service_salas[opt_sala-1][0],
                            'fecha_req': fecha_req    
                        }
                        if GetFromService(SERVICE_HOR_USADO_SALA) == 'OK':
                            SendToService(SERVICE_HOR_USADO_SALA, data_sala)

                            while True: 
                                data_service_horario_usado = socket.recv(390)
                                data_service_salas = data_service_salas[12:]
                                break
                            #-------------------------------------HORARIOS DISPONIBLES DE UNA SALA EN UN DIA ESPECIFICOS-------------------------#
                            HORARIOS_DISP = []
                            print(f'Horarios disponibles en el día {fecha_req}')
                            for i in len(HORARIOS):
                                if(data_service_horario_usado != HORARIOS[i]):
                                    HORARIOS_DISP.append(HORARIOS[i])
                                    print(f'{i+1}. {HORARIOS[i]}')
                            
                            opt_horario = int(input('>> '))
                            
                            menu_conf_reserva = True
                            PARTICIPANTES = []
                            while menu_conf_reserva: 
                                #=-------------------------------------------------MENU CONFIRMACION DE RESERVA-----------------------------------------------------#
                                print('Que desea hacer:')
                                print('1. Agregar participante a la reunion')
                                print('2. Confirmar reserva (no puede ingresar más participantes)')
                                print('3. No realizar reserva y salir')
                                opt3 = int(input('>> '))
                                
                                if(opt3 == 1): #Ingresar participante
                                    print('Ingrese datos del participante:')
                                    rut_p = input('RUT: ')
                                    nombre_p = input('Nombre: ')
                                    correo_p = input('Email: ')
                                    
                                    if not rut_p or not nombre_p or not correo_p:
                                        print('No se pudo ingresar al participante porque un campo no es correcto.')
                                    else:
                                        PARTICIPANTES.append({
                                            'rut': rut_p,
                                            'nombre': nombre_p,
                                            'correo': correo_p,
                                            'reserva_id': data_service_salas[opt_sala-1][0]                                            
                                        })
                                        print('Participante agregado')
                                elif(opt3 == 2): #Confirmar reserva
                                    if GetFromService(SERVICE_CONFIRM_RES) == 'OK' and GetFromService(SERVICE_ADD_PARTICIPANTE_RESERV) == 'OK':
                                        print('Confirmando reserva...')
                                        data_confirma_reserva = {
                                            'inicia': f'{fecha_req} {HORARIOS_DISP[opt_horario][:5]}',
                                            'termina': f'{fecha_req} {HORARIOS_DISP[opt_horario][8:]}',
                                            'anfitrion_rut': rut_usuario,
                                            'sala_id': data_service_salas[opt_sala-1][0]
                                        }
                                        SendToService(SERVICE_CONFIRM_RES, data_confirma_reserva)

                                        while True: 
                                            data_service_horario_usado = socket.recv(390)
                                            break
                                        #AGREGA A LOS PARTICIPANTES EN LA BD DESPUES DE AGREGAR LA RESERVA EN LA BD

                                        print('Agregando los participantes a la reserva realizada...')
                                        for i in len(PARTICIPANTES):
                                            data_participante = {
                                                'rut': PARTICIPANTES[i]['rut'],
                                                'nombre': PARTICIPANTES[i]['nombre'],
                                                'correo': PARTICIPANTES[i]['correo'],
                                                'reserva_id': data_service_salas[opt_sala-1][0]
                                            }
                                            SendToService(SERVICE_ADD_PARTICIPANTE_RESERV, data_participante)

                                            while True: 
                                                data_service_horario_usado = socket.recv(390)
                                                break


                                        print('Reserva realizada, ¡adios!')
                                        menu_conf_reserva = False
                                    else: 
                                        print('Servicio de reserva no disponible')  
                                        menu_conf_reserva = False
                                else:
                                    print('¡ADIOS!')
                                    menu_conf_reserva = False
                        else: 
                            print('Servicio de reserva no disponible')    
                    else: 
                        print('Servicio de reserva no disponible')

                elif(opt2 == 2): #Cancela reserva ya guardada en la BD
                    print('Indique la reserva que desea cancelar:')
                    if GetFromService(SERVICE_RESERV_REALIZADAS) == 'OK' and GetFromService(SERVICE_CANCEL_RESERV) == 'OK':
                            data_reservas_realiz = {
                                'rut_anfitrion': rut_usuario
                            }
                            SendToService(SERVICE_RESERV_REALIZADAS, data_reservas_realiz)
                            
                            while True: 
                                reservas_realizadas = socket.recv(390)
                                break
                            
                            for i in len(reservas_realizadas):
                                print(f'{i+1}. {reservas_realizadas[i][1]}')
                            opt_reserva_cancel = int(input('>> '))
                            
                            for i in len(reservas_realizadas):
                                if reservas_realizadas[opt_reserva_cancel-1]==reservas_realizadas[i]:
                                    reserva_id_toCancel = reservas_realizadas[i][0]

                            data_cancel_reserva = {
                                'reserva_id': reserva_id_toCancel
                            }

                            SendToService(SERVICE_CANCEL_RESERV, data_cancel_reserva)
                            while True: 
                                reservas_realizadas = socket.recv(390)
                                break
                            print('Reserva cancelada.')
                else:
                    print('¡ADIOS!')
                    pass