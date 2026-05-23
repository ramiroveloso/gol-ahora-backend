================================================================================
DIAGRAMA DE CLASES: GOL AHORA
================================================================================

Usuario:
 - Id
 - Nombre
 - Apellido
 - Direccion
 - Telefono
 - Email
 - Rol
 + RegistrarUsuario()
 + ModificarUsuario()
 + ConsultarUsuario()
 + EliminarUsuario()
 + ImprimirDatos()

ProfesorEntrenador:
 - Id
 - Nombre
 - Apellido
 - Telefono
 - Email
 - CertificacionDeportiva
 + RegistrarProfesor()
 + ModificarProfesor()
 + ConsultarProfesor()
 + EliminarProfesor()
 + VerificarCertificacion()

Cancha:
 - IdCancha
 - Numero
 - TipoCancha
 - Superficie
 - Capacidad
 - EstadoDisponibilidad
 - DuracionMaximaReserva
 + RegistrarCancha()
 + ModificarCancha()
 + ConsultarCancha()
 + EliminarCancha()
 + VerificarDisponibilidad()

Reserva:
 - IdReserva
 - FechaReserva
 - HoraInicio
 - HoraFin
 - Estado
 - AntelacionCancelacion
 + RegistrarReserva()
 + ModificarReserva()
 + CancelarReserva()
 + ConsultarDisponibilidad()

ClaseEntrenamiento:
 - IdClase
 - Horario
 - MaximoAlumnos
 - TipoClase
 + ProgramarClase()
 + ConsultarCupo()
 + AsignarProfesor()

Asistencia:
 - IdAsistencia
 - Fecha
 - EstadoAsistencia
 + RegistrarAsistencia()
 + GenerarReporteAsistencia()

LigaTorneo:
 - IdCompetencia
 - NombreCompetencia
 - TipoCompetencia
 - Fixture
 + RegistrarCompetencia()
 + GestionarInscripcion()
 + GenerarCuadroTorneo()
 + RegistrarResultado()

Cobro:
 - IdCobro
 - Monto
 - FechaCobro
 - MetodoPago
 - EstadoPago
 + RegistrarCobro()
 + ModificarCobro()
 + ConsultarCobro()
 + AplicarDescuento()

ReciboPago:
 - IdRecibo
 - Detalle
 - FechaEmision
 + RegistrarRecibo()
 + ConsultarRecibo()
 + ImprimirRecibo()

Descuento:
 - IdDescuento
 - TipoDescuento
 - Porcentaje
 + ConfigurarDescuento()
 + GestionarDescuento()

================================================================================
RELACIONES ENTRE ENTIDADES
================================================================================

 - Usuario 1 === * Reserva: Un usuario puede realizar muchas reservas en el sistema.
 - Cancha 1 === * Reserva: Una cancha puede tener asignadas múltiples reservas en diferentes horarios.
 - Usuario 1 === * Cobro: Un usuario puede registrar muchos cobros asociados a sus actividades o alquileres.
 - Cobro 1 === 1 ReciboPago: Todo cobro registrado y validado genera obligatoriamente un único recibo de pago.
 - Descuento 1 === * Cobro: Un descuento puede ser aplicado a múltiples cobros según las políticas del club.
 - Usuario * === * LigaTorneo: Muchos usuarios pueden inscribirse y participar en muchas ligas y torneos.
 - ProfesorEntrenador 1 === * ClaseEntrenamiento: Un profesor o entrenador puede tener asignado el dictado de muchas clases.
 - ClaseEntrenamiento * === * Usuario: Muchos usuarios pueden asistir a muchas clases y entrenamientos.
 - ClaseEntrenamiento 1 === 1 Asistencia: Cada clase o entrenamiento programado genera un registro para el control de asistencia.
 - ProfesorEntrenador 1 === * Usuario: Un profesor puede ser asignado de forma particular a múltiples usuarios.