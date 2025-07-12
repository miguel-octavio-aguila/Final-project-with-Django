# admin.py

# Se importa el framework de administración de Django.
from django.contrib import admin
# Se importan todos los modelos de la app para poder registrarlos en el sitio de administración.
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


# === Clases de Administración Inline ===
# Las clases "Inline" permiten editar modelos relacionados en la misma página que el modelo "padre".
# Esto mejora enormemente la experiencia de usuario para el administrador.

# Permite editar Preguntas directamente desde la página de un Curso o Lección.
class QuestionInline(admin.StackedInline):
    model = Question # Especifica que el modelo a editar "inline" es Question.
    extra = 1        # Muestra 1 formulario vacío extra para añadir una nueva pregunta.

# Permite editar Opciones (Choices) directamente desde la página de una Pregunta.
class ChoiceInline(admin.StackedInline):
    model = Choice # El modelo a editar es Choice.
    extra = 1      # Muestra 1 formulario vacío extra para una nueva opción.

# Permite editar Lecciones directamente desde la página de un Curso.
class LessonInline(admin.StackedInline):
    # 'admin.StackedInline' muestra cada formulario de lección en un bloque vertical.
    # La alternativa, 'admin.TabularInline', los mostraría en una tabla más compacta.
    model = Lesson # El modelo a editar es Lesson.
    extra = 5      # Muestra 5 formularios vacíos para añadir rápidamente varias lecciones a un curso.


# === Clases de Personalización ModelAdmin ===
# Estas clases se usan para personalizar la apariencia y funcionalidad del admin para modelos específicos.

# Personalización para el modelo Course.
class CourseAdmin(admin.ModelAdmin):
    # 'inlines' incrusta los formularios de los modelos especificados.
    # Aquí, en la página de edición de un Curso, también se podrán editar sus Lecciones.
    inlines = [LessonInline]
    # 'list_display' personaliza las columnas que se muestran en la lista de cursos.
    list_display = ('name', 'pub_date')
    # 'list_filter' añade una barra lateral para filtrar los cursos por el campo 'pub_date'.
    list_filter = ['pub_date']
    # 'search_fields' añade una barra de búsqueda que buscará en los campos 'name' y 'description'.
    search_fields = ['name', 'description']


# Personalización para el modelo Lesson.
class LessonAdmin(admin.ModelAdmin):
    # En la lista de lecciones, solo se mostrará la columna 'title'.
    list_display = ['title']


# Personalización para el modelo Question.
class QuestionAdmin(admin.ModelAdmin):
    # En la página de edición de una Pregunta, se podrán editar sus Opciones (Choices).
    inlines = [ChoiceInline]
    # En la lista de preguntas, se mostrará el texto de la pregunta.
    list_display = ['question']


# === Registro de Modelos en el Sitio de Administración ===

# Se registra el modelo Course usando su clase de personalización CourseAdmin.
admin.site.register(Course, CourseAdmin)
# Se registra el modelo Lesson usando su clase de personalización LessonAdmin.
admin.site.register(Lesson, LessonAdmin)
# Se registra el modelo Question usando su clase de personalización QuestionAdmin.
admin.site.register(Question, QuestionAdmin)
# Los siguientes modelos se registran sin una clase de personalización,
# por lo que usarán la interfaz por defecto del admin de Django.
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Instructor)
admin.site.register(Learner)