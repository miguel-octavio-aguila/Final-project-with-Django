# views.py

# Importaciones de Django para renderizar plantillas y manejar redirecciones.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic # Para Vistas Basadas en Clases (CBV) genéricas.

# Importaciones de los modelos de la aplicación para interactuar con la base de datos.
from .models import Course, Enrollment, Question, Choice, Submission
# Importación del modelo de usuario por defecto de Django y funciones de autenticación.
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

# Importación del sistema de logging para registrar eventos o errores.
import logging
logger = logging.getLogger(__name__) # Obtiene una instancia del logger para este archivo.

# === Vistas de Autenticación (Basadas en Funciones) ===

def registration_request(request):
    context = {}
    if request.method == 'GET':
        # Si la petición es GET, simplemente muestra el formulario de registro.
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Si la petición es POST, procesa los datos del formulario.
        username = request.POST['username']
        # Se verifica si el nombre de usuario ya existe en la base de datos.
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            user_exist = False
        
        if not user_exist:
            # Si el usuario no existe, se crea con los datos proporcionados.
            # create_user se encarga de hashear la contraseña de forma segura.
            user = User.objects.create_user(
                username=username,
                first_name=request.POST['firstname'],
                last_name=request.POST['lastname'],
                password=request.POST['psw']
            )
            # Se inicia la sesión para el usuario recién creado.
            login(request, user)
            # Se redirige al usuario a la página principal.
            return redirect("onlinecourse:index")
        else:
            # Si el usuario ya existe, se devuelve al formulario con un mensaje de error.
            context['message'] = "El nombre de usuario ya existe."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        # 'authenticate' verifica si las credenciales son válidas. Devuelve un objeto User o None.
        user = authenticate(username=username, password=password)
        if user is not None:
            # Si las credenciales son válidas, se inicia la sesión.
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            # Si no, se muestra un mensaje de error.
            context['message'] = "Usuario o contraseña no válidos."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    # Si es GET, se muestra el formulario de login.
    return render(request, 'onlinecourse/user_login_bootstrap.html', context)

def logout_request(request):
    # 'logout' finaliza la sesión del usuario actual.
    logout(request)
    return redirect('onlinecourse:index')

# === Vistas Basadas en Clases (CBV) para Cursos ===

# Vista para listar los cursos. Hereda de la vista genérica ListView.
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list' # Nombre de la variable que contendrá la lista de cursos en la plantilla.

    # Sobrescribe el método que obtiene el conjunto de datos (queryset).
    def get_queryset(self):
        user = self.request.user
        # Obtiene los 10 cursos con más inscripciones.
        courses = Course.objects.order_by('-total_enrollment')[:10]
        if user.is_authenticated:
            # Para cada curso, verifica si el usuario actual está inscrito.
            # El resultado se almacena en el atributo 'is_enrolled' del objeto curso.
            for course in courses:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses

# Vista para mostrar los detalles de un curso. Hereda de DetailView.
class CourseDetailView(generic.DetailView):
    model = Course # El modelo del cual se mostrará un detalle.
    template_name = 'onlinecourse/course_detail_bootstrap.html'

# === Vistas Basadas en Funciones (FBV) para Lógica de Cursos ===

# Función auxiliar para comprobar si un usuario está inscrito en un curso.
def check_if_enrolled(user, course):
    # Realiza una consulta para contar las inscripciones que coincidan con el usuario y el curso.
    return Enrollment.objects.filter(user=user, course=course).count() > 0

# Vista para manejar la inscripción de un usuario a un curso.
def enroll(request, course_id):
    # get_object_or_404 busca un objeto y devuelve un error 404 si no lo encuentra.
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    # Si el usuario está autenticado y no está ya inscrito...
    if user.is_authenticated and not check_if_enrolled(user, course):
        # ...se crea una nueva inscripción.
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    # Redirige al usuario de vuelta a la página de detalles del curso.
    # reverse() construye la URL a partir del nombre definido en urls.py.
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))

# === Vistas para Exámenes ===

# Vista para procesar el envío de un examen.
def submit(request, course_id):
    user = request.user
    # Se obtienen los objetos de curso e inscripción correspondientes.
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    # Se crea un nuevo objeto Submission ligado a la inscripción.
    submission = Submission.objects.create(enrollment=enrollment)
    # Se extraen los IDs de las respuestas seleccionadas y se asocian al envío.
    # .set() es el método para actualizar una relación ManyToMany.
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id

    # Se redirige a la página de resultados, pasando los IDs necesarios.
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course_id, submission_id,)))

# Función auxiliar para extraer las respuestas del formulario del examen.
def extract_answers(request):
    submitted_answers = []
    # Itera sobre todas las claves en los datos POST del formulario.
    for key in request.POST:
        # Busca claves que comiencen con 'choice', una convención para nombrar los inputs de las respuestas.
        if key.startswith('choice'):
            # Extrae el valor (que es el ID de la Choice) y lo añade a la lista.
            choice_id = int(request.POST[key])
            submitted_answers.append(choice_id)
    return submitted_answers

# Vista para mostrar los resultados de un examen.
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    # Se obtienen todas las opciones que el usuario seleccionó en este envío.
    selected_choices = submission.choices.all()

    total_score = 0
    # Se obtienen todas las preguntas del curso.
    questions = course.question_set.all()

    # Se itera sobre cada pregunta para calificarla.
    for question in questions:
        # Se obtienen las opciones correctas para la pregunta actual.
        correct_choices = question.choice_set.filter(is_correct=True)
        # Se obtienen las opciones que el usuario seleccionó para la pregunta actual.
        user_choices_for_question = selected_choices.filter(question=question)

        # Se comparan los conjuntos (sets) de opciones. Usar sets es robusto porque no importa el orden.
        # Si el conjunto de opciones correctas es idéntico al conjunto de opciones seleccionadas por el usuario...
        if set(correct_choices) == set(user_choices_for_question):
            # ...el usuario obtiene el puntaje de esa pregunta.
            total_score += question.grade

    context['course'] = course
    context['grade'] = total_score
    context['choices'] = selected_choices

    # Se renderiza la plantilla de resultados con el contexto calculado.
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)