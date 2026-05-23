# INSTRUCCIONES DE CONTEXTO OBLIGATORIAS PARA EL AGENTE

Siempre, antes de escribir cualquier código, requerimiento, caso de prueba o modificación en este proyecto ("Gol Ahora"), debés leer y aplicar las siguientes reglas. Está prohibido desviarse de esta estructura.
Siempre preguntar para confirmar si vas a hacer un cambio.
[PRIORIDAD-MAXIMA]Cada vez que se tenga que hacer una tarea investigar bien el contexto y hacer las preguntas necesarias para entender bien la finalidad de la tarea 

## 🛠️ Stack Tecnológico
- Backend: Python 3 con Django y Django REST Framework.
- Base de Datos: PostgreSQL.
- Frontend: React con JavaScript.

## 📐 Reglas Estrictas de Ingeniería (Cátedra UNAJ)
1. Requerimientos Funcionales: Estructura exacta "El sistema debe [VERBO EN INFINITIVO] [OBJETO]". Prohibido usar "Gestionar" o "Administrar". Cada acción del ABML es atómica e individual.
2. Diagrama de Clases: Respetar fielmente las entidades y métodos definidos en la estructura del proyecto (revisar CLASES.md).
3. Base de Datos: Usar migraciones nativas de Django y el ORM. Prohibido Querys SQL planas (Inyección SQL).