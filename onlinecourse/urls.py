# urls.py

# Se importa la función 'path' para definir cada ruta individual.
from django.urls import path
# Se importa 'settings' para acceder a las configuraciones del proyecto, como las rutas de archivos multimedia.
from django.conf import settings
# Se importa 'static' para generar la URL necesaria para servir archivos estáticos (media) en modo de desarrollo.
from django.conf.urls.static import static
# Se importa el archivo de vistas (views.py) de la misma aplicación para poder enlazar las rutas a la lógica de las vistas.
from . import views

# app_name establece un "espacio de nombres" para las URLs de esta aplicación.
# Permite referenciar las URLs de forma única, ej: 'onlinecourse:index', evitando colisiones con otras apps.
app_name = 'onlinecourse'

# urlpatterns es una lista que Django recorre para encontrar una coincidencia con la URL solicitada.
urlpatterns = [
    # Cada 'path' define una regla de enrutamiento.
    # route: El patrón de la URL a buscar. Una cadena vacía '' representa la raíz de la app.
    # view: La función o clase de vista que manejará la lógica para esta ruta.
    # name: Un nombre único para esta ruta, usado para la resolución inversa de URLs (reverse lookup).

    # Ruta raíz de la app, muestra la lista de cursos usando una Vista Basada en Clase (CBV).
    path(route='', view=views.CourseListView.as_view(), name='index'),
    # Ruta para la página de registro de usuarios.
    path('registration/', views.registration_request, name='registration'),
    # Ruta para la página de inicio de sesión.
    path('login/', views.login_request, name='login'),
    # Ruta para gestionar el cierre de sesión.
    path('logout/', views.logout_request, name='logout'),

    # Ruta para ver los detalles de un curso específico.
    # <int:pk> captura un entero de la URL y lo pasa a la vista como un argumento llamado 'pk' (Primary Key).
    # .as_view() es necesario para las Vistas Basadas en Clase (CBV).
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    
    # Ruta para inscribir a un usuario en un curso.
    # Captura el ID del curso para saber en cuál inscribir al usuario.
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    # Ruta para que un usuario envíe las respuestas de un examen de un curso.
    path('<int:course_id>/submit/', views.submit, name="submit"),

    # Ruta para mostrar el resultado de un envío (submission) específico.
    # Requiere el ID del curso y el ID del envío para localizar el resultado correcto.
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name="exam_result"),

# Se añade la configuración para servir archivos multimedia (como las imágenes de los cursos) durante el desarrollo.
# Esto no es para un entorno de producción.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)