# planning.md

## 📌 PLAN DE DESARROLLO BACKEND: "GOL AHORA"

Este plan detalla los módulos, la estructura de aplicaciones en Django y los Requerimientos Funcionales del Backend (RF-BACK) necesarios para construir la API transaccional que consumirá el frontend en React.

---

## 🛠️ CONFIGURACIÓN INICIAL DEL ENTORNO

* [ ] Inicializar repositorio Git.
* [ ] Crear entorno virtual Python y configurar contenedor Docker para desarrollo en Debian.
* [ ] Instalar dependencias base: `django`, `djangorestframework`, `django-cors-headers`, `psycopg2-binary` (para PostgreSQL).
* [ ] Configurar el archivo `settings.py` (CORS, Base de datos, Apps).

---

## 📦 MÓDULOS DEL SISTEMA Y REQUERIMIENTOS BACKEND

### 1. App: `authentication` (Gestión de Usuarios y Seguridad)

*Módulo encargado del registro, control de acceso, asignación de roles (Socio, Empleado, Administrador) y persistencia de cuentas.*

* [ ] **RF-BACK-001:** El sistema debe registrar un nuevo usuario con contraseña encriptada (Bcrypt/PBKDF2).
* [ ] **RF-BACK-002:** El sistema debe autenticar las credenciales de un usuario y retornar un Token de acceso (JWT).
* [ ] **RF-BACK-003:** El sistema debe revocar el Token de acceso al solicitar el cierre de sesión.
* [ ] **RF-BACK-004:** El sistema debe modificar los datos del perfil de un usuario.
* [ ] **RF-BACK-005:** El sistema debe realizar la baja lógica de un usuario (cambiar estado a inactivo).
* [ ] **RF-BACK-006:** El sistema debe consultar los datos de un usuario por su ID único.

### 2. App: `fields` (Gestión de Canchas e Instalaciones)

*Módulo encargado del inventario de las canchas del complejo, especificaciones de deportes y disponibilidad física.*

* [ ] **RF-BACK-007:** El sistema debe registrar una nueva cancha (Número, tipo de suelo, deporte, precio base por hora).
* [ ] **RF-BACK-008:** El sistema debe modificar los datos de una cancha existente.
* [ ] **RF-BACK-009:** El sistema debe realizar la baja de una cancha.
* [ ] **RF-BACK-010:** El sistema debe listar todas las canchas activas filtradas por tipo de deporte.

### 3. App: `bookings` (Gestión de Turnos y Reservas)

*Módulo crítico transaccional. Se encarga del control de horarios, asignación de canchas a usuarios y prevención estricta de solapamientos.*

* [ ] **RF-BACK-011:** El sistema debe crear una reserva de turno vinculando un usuario, una cancha, una fecha y una hora específica.
* [ ] **RF-BACK-012:** El sistema debe denegar la creación de una reserva si la cancha elegida ya posee un turno asignado en ese rango horario.
* [ ] **RF-BACK-013:** El sistema debe denegar la creación de una reserva si el usuario solicitante posee deudas pendientes en su cuenta.
* [ ] **RF-BACK-014:** El sistema debe cancelar una reserva modificando su estado a "Cancelada".
* [ ] **RF-BACK-015:** El sistema debe consultar la grilla de turnos disponibles y ocupados para una fecha determinada.

### 4. App: `finance` (Gestión de Cobros y Cajas)

*Módulo encargado del procesamiento de pagos, control de saldos y la generación del entregable físico/digital.*

* [ ] **RF-BACK-016:** El sistema debe registrar un cobro asociado a una reserva de turno (Monto, método de pago, fecha-hora, estado "Aprobado").
* [ ] **RF-BACK-017:** El sistema debe emitir un recibo digital en formato JSON estructurado con los datos del cobro.
* [ ] **RF-BACK-018:** El sistema debe generar un archivo para impresión física (Ticket de pago) ante la confirmación del cobro.
* [ ] **RF-BACK-019:** El sistema debe consultar el historial de cobros realizados entre un rango de fechas (Cierre de caja).

---

## 🚀 CRONOGRAMA DE EJECUCIÓN (ROADMAP)

1. **FASE 1:** Modelado de Base de Datos y app `authentication`. (Prueba de endpoints con el Django Admin y Postman).
2. **FASE 2:** Desarrollo de la app `fields` y lógicas CRUD simples.
3. **FASE 3:** Implementación del núcleo duro transaccional en `bookings` (Validación estricta de no superposición de horarios).
4. **FASE 4:** Integración de la lógica de pagos en `finance` y generación de respuestas para tickets.
5. **FASE 5:** Testing de integración automatizado en Django.

---
