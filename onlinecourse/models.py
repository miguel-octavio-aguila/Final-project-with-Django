# models.py

# Se importa el módulo 'sys' para interactuar con el intérprete de Python, usado aquí para detener la ejecución si Django no está instalado.
import sys
# Se importa 'now' de django.utils.timezone para asignar la fecha y hora actual a los campos de fecha, asegurando consistencia con la zona horaria del proyecto.
from django.utils.timezone import now
try:
    # Se importa el módulo 'models' de Django, que es el núcleo del ORM (Object-Relational Mapper) y permite definir la estructura de la base de datos como clases de Python.
    from django.db import models
except Exception:
    # Bloque de manejo de errores para el caso en que el entorno no tenga Django instalado.
    print("Hubo un error al cargar los módulos de Django. ¿Tienes Django instalado?")
    sys.exit()

# Se importa 'settings' para poder referenciar el modelo de usuario personalizado del proyecto (AUTH_USER_MODEL), una buena práctica para la reutilización de apps.
from django.conf import settings
# Se importa 'uuid' para la posible generación de identificadores únicos, aunque no se usa en este fragmento.
import uuid


# === Modelo Instructor ===
# Representa a un profesor o creador de contenido en la plataforma.
class Instructor(models.Model):
    # Relación de uno a uno (implícita por ForeignKey) con el modelo de usuario de Django.
    # Cada instructor ES un usuario del sistema.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Referencia al modelo de usuario activo en el proyecto.
        on_delete=models.CASCADE,  # Si el usuario se elimina, su perfil de instructor también se eliminará.
    )
    # Campo booleano para indicar si el instructor es de tiempo completo.
    full_time = models.BooleanField(default=True)
    # Campo numérico para almacenar el número total de estudiantes asociados a este instructor.
    total_learners = models.IntegerField()

    # Método para la representación en cadena del objeto.
    # Es crucial para que en el admin de Django y en otras partes se muestre un nombre legible (el nombre de usuario).
    def __str__(self):
        return self.user.username


# === Modelo Learner (Estudiante) ===
# Representa a un usuario que consume contenido (un estudiante).
class Learner(models.Model):
    # Relación de uno a uno con el modelo de usuario. Cada estudiante ES un usuario.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Si se elimina el usuario, el perfil de estudiante se elimina.
    )
    # Definición de constantes para las opciones del campo 'occupation'.
    # Esto evita errores tipográficos y hace el código más legible y mantenible.
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    # Creación de una tupla de tuplas para ser usada en el atributo 'choices' del campo.
    # El primer elemento de cada tupla interna se almacena en la BD, el segundo se muestra al usuario.
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    # Campo de texto que almacena la ocupación del estudiante.
    occupation = models.CharField(
        null=False,             # No puede ser nulo en la base de datos.
        max_length=20,          # Longitud máxima del texto.
        choices=OCCUPATION_CHOICES, # Restringe los valores posibles a los definidos arriba.
        default=STUDENT         # Valor por defecto si no se especifica uno.
    )
    # Campo para almacenar una URL, como un perfil de LinkedIn o GitHub.
    social_link = models.URLField(max_length=200)

    # Representación en cadena que combina el nombre de usuario y su ocupación.
    def __str__(self):
        return self.user.username + "," + self.occupation


# === Modelo Course (Curso) ===
# Define la estructura de un curso en la plataforma.
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    # Campo para subir imágenes. 'upload_to' especifica la subcarpeta dentro del directorio de medios donde se guardarán.
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True) # Fecha de publicación del curso.
    # Relación de muchos a muchos con Instructor. Un curso puede tener varios instructores y un instructor puede impartir varios cursos.
    instructors = models.ManyToManyField(Instructor)
    # Relación de muchos a muchos con el modelo de Usuario, pero con una tabla intermedia personalizada llamada 'Enrollment'.
    # Esto permite almacenar información adicional sobre la relación (ej. la fecha de inscripción, la calificación).
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False # Este es un atributo de instancia de Python, NO un campo de la base de datos. Se usaría para lógica en tiempo de ejecución.

    def __str__(self):
        return "Name: " + self.name + "," + "Description: " + self.description


# === Modelo Lesson (Lección) ===
# Representa una unidad de contenido dentro de un curso.
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0) # Para definir el orden de las lecciones dentro del curso.
    # Relación de muchos a uno con Course. Cada lección pertenece a un único curso.
    course = models.ForeignKey(Course, on_delete=models.CASCADE) # Si el curso se borra, sus lecciones también.
    # Campo de texto de gran capacidad para el contenido principal de la lección.
    content = models.TextField()


# === Modelo Enrollment (Inscripción) ===
# Esta es la tabla intermedia ('through model') que conecta a los Usuarios con los Cursos.
# Permite añadir metadatos a la inscripción.
class Enrollment(models.Model):
    # Definición de constantes para los modos del curso.
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    # Claves foráneas que crean la relación muchos a muchos.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Campo de fecha que se autocompleta con la fecha actual al crear la inscripción.
    date_enrolled = models.DateField(default=now)
    # Modo de inscripción (de auditoría, con honores, etc.).
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    # Calificación que el usuario le da al curso.
    rating = models.FloatField(default=5.0)


# === Modelo Question (Pregunta) ===
# Representa una pregunta de un examen o cuestionario.
class Question(models.Model):
    # Cada pregunta pertenece a un curso.
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.CharField(max_length=200) # El texto de la pregunta.
    grade = models.IntegerField(default=50)     # El puntaje que otorga esta pregunta.

    def __str__(self):
        return 'Question: ' + self.question

    # Método de instancia para calcular si el estudiante obtiene el puntaje de esta pregunta.
    def is_get_score(self, selected_ids):
        # self.choice_set es el "RelatedManager" que permite acceder a todas las Choices relacionadas con esta Question.
        # Primero, cuenta cuántas opciones correctas existen en total para esta pregunta.
        all_answers = self.choice_set.filter(is_correct=True).count()
        # Luego, cuenta cuántas de las opciones seleccionadas por el usuario (cuyos IDs vienen en selected_ids) son correctas.
        # 'id__in' es un "field lookup" que crea una consulta SQL `WHERE id IN (...)`.
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        # La lógica es estricta: el usuario obtiene el puntaje solo si el número de respuestas correctas que seleccionó es igual al número total de respuestas correctas posibles.
        # Esto implica que debe seleccionar TODAS las correctas y NINGUNA incorrecta (asumiendo que las incorrectas no se cuentan aquí).
        if all_answers == selected_correct:
            return True
        else:
            return False

# === Modelo Choice (Opción) ===
# Representa una opción de respuesta para una Pregunta.
class Choice(models.Model):
    # Cada opción pertenece a una única pregunta.
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=200) # El texto de la opción.
    # Campo booleano que marca si esta es una respuesta correcta.
    is_correct = models.BooleanField(default=False)

# === Modelo Submission (Envío) ===
# Representa el envío de un conjunto de respuestas por parte de un estudiante.
# Una inscripción puede tener múltiples envíos (intentos).
# Un envío tiene múltiples opciones seleccionadas.
# Una opción puede pertenecer a múltiples envíos (si varios estudiantes la eligen).
class Submission(models.Model):
    # El envío está ligado a una inscripción específica (un usuario en un curso).
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    # Relación de muchos a muchos con Choice. Esto modela las respuestas seleccionadas por el usuario.
    # Django creará una tabla intermedia para vincular los IDs de Submission con los IDs de Choice.
    choices = models.ManyToManyField(Choice)