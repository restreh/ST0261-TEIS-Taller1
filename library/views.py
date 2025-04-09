from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from .models import Book, Review, Rating, BookHistory, BookDetails
from django.urls import reverse
import datetime
from datetime import date, timedelta
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from .forms import LibroForm, DetailsForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django import forms
from .models import User
from django.contrib.auth import login, authenticate
from django.template import loader

from django.contrib.auth.forms import UserCreationForm

from .services import LibraryService

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name')
    email = forms.EmailField(max_length=254, required=True, help_text='Email address')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

def home(request):
    cancel_reservation_automatic(request)
    check_rented(request)
    
    # Obtiene el término de búsqueda y la opción de ordenación desde la solicitud
    searchTerm = request.GET.get('searchBook')
    sort_option = request.GET.get('sort')
    
    # Filtra los libros según el término de búsqueda si existe
    if searchTerm and searchTerm != 'None':
        books = Book.objects.filter(title__icontains=searchTerm)
    else:
        books = Book.objects.all()
    
    # Aplica la ordenación según la opción seleccionada
    if sort_option == 'asc':
        books = books.order_by('rating_average')
    elif sort_option == 'desc':
        books = books.order_by('-rating_average')
    elif sort_option == 'genre':
        books = books.order_by('bookdetails__genre')
    elif sort_option == 'subject':
        books = books.order_by('bookdetails__subject')
    
    # Renderiza la plantilla con los libros filtrados y ordenados, y los parámetros de búsqueda y ordenación
    return render(request, 'home.html', {'books': books, 'searchTerm': searchTerm, 'sort_option': sort_option})


@login_required
def rate_book(request):
    cancel_reservation_automatic(request)
    check_rented(request)
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        rating = request.POST.get('rating')
        
        if not rating:
            return HttpResponseBadRequest("No se ha proporcionado una calificación.")
        
        rating = int(rating)
        
        book = get_object_or_404(Book, id=book_id)
        user = request.user
        
        # Verificar si el usuario ya ha dejado un rating para este libro
        existing_rating = Rating.objects.filter(book=book, user=user).exists()
        if existing_rating:
            return HttpResponseBadRequest("Ya has dejado un rating para este libro.")
        
        # Crear el rating
        Rating.objects.create(book=book, user=user, value=rating)
        
        # Calcular el rating promedio del libro
        ratings = Rating.objects.filter(book=book)
        total_ratings = ratings.count()
        sum_ratings = sum(rating.value for rating in ratings)
        book.rating_average = sum_ratings / total_ratings
        book.save()
        
    return redirect('home')
 

@login_required
def submit_review(request):
    cancel_reservation_automatic(request)
    check_rented(request)
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        review_text = request.POST.get('reviewText')
        book = Book.objects.get(id=book_id)
        # Aquí asegúrate de asignar correctamente el usuario al crear la instancia de Review
        Review.objects.create(book=book, user=request.user, text=review_text)
        # Redirige a la página de descripción del libro con el ancla del comentario
        return HttpResponseRedirect(reverse('book_details', args=(book_id,)) + '#reviews')
    else:
        return redirect('home')

def about(request):
    cancel_reservation_automatic(request)
    check_rented(request)
    return render(request, 'about.html')

def book_details(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)
    details = BookDetails.objects.get(book = book)
    reviews = Review.objects.filter(book=book)
    return render(request, 'book_description.html', {'book': book,'details':details, 'reviews': reviews})


"""def book_description(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'book_description.html', {'book': book})"""

def adminrent(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)
    
    return render(request, 'adminrent.html', {'book': book})


def change_availability(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)
    
    # Cambiar el estado de disponibilidad
    if book.available:
        book.available = False
        book.availability = datetime.date.today() + datetime.timedelta(days=31)  # Establecer la disponibilidad en 31 días desde hoy
    else:
        book.available = True
        book.availability = None
    
    book.save()
    
    # Redirigir a la página de descripción del libro actualizado
    return HttpResponseRedirect(reverse('book_details', args=(book_id,)))

"""
@login_required
def reserve_book(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)
    user = request.user
    
    # Verificar si el libro está reservado y si el usuario actual realizó esa reserva
    if book.reserved and book.reserved_by != user and not user.is_staff:
        # Mostrar un mensaje de error en la misma página
        messages.error(request, "You are not authorized to cancel this reservation.")
        # Obtener las reseñas del libro para pasarlas a la plantilla
        reviews = Review.objects.filter(book=book)
        # Renderizar la página de descripción del libro actualizada con el mensaje de error y las reseñas
        return render(request, 'book_description.html', {'book': book, 'reviews': reviews, 'error_message': "You are not authorized to cancel this reservation."})
    
    # Cambiar el estado de reserva
    if book.reserved:
        book.reserved = False
        book.reserved_date = None
        book.reserved_by = None  # Limpiar el campo del usuario que reservó
    else:
        book.reserved = True
        book.reserved_date = datetime.date.today() + datetime.timedelta(days=7)  # Establecer la fecha de reserva en 7 días desde hoy
        book.reserved_by = user  # Establecer el usuario actual como el que reservó
    
    book.save()
    
    # Redirigir a la página de descripción del libro actualizado
    return HttpResponseRedirect(reverse('book_details', args=(book_id,)))
"""

@login_required
def reserve_book(request, book_id, library_service=LibraryService()):
    # Usar los métodos a través de la interfaz
    library_service.cancel_reservation_automatic()
    library_service.check_rented()

    book = get_object_or_404(Book, pk=book_id)
    user = request.user

    if book.reserved and book.reserved_by != user and not user.is_staff:
        reviews = Review.objects.filter(book=book)
        messages.error(request, "You are not authorized to cancel this reservation.")
        return render(request, 'book_description.html', {
            'book': book,
            'reviews': reviews,
            'error_message': "You are not authorized to cancel this reservation."
        })

    if book.reserved:
        book.reserved = False
        book.reserved_date = None
        book.reserved_by = None
    else:
        book.reserved = True
        book.reserved_date = datetime.today().date() + timedelta(days=7)
        book.reserved_by = user

    book.save()

    return HttpResponseRedirect(reverse('book_details', args=(book_id,)))



def change_real_availability(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)
    
    if book.real_available:
        book.real_available = False
        book.real_availability = datetime.date.today() + datetime.timedelta(days=14)
    else:
        book.real_available = True
        book.real_availability = None 
        
    book.save()
    
    return HttpResponseRedirect(reverse('book_details', args=(book_id,)))

def verify_availability(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)
    
    if book.real_available and not book.reserved:
        book.available = True
        book.availability = None
    elif book.real_available and book.reserved:
        book.available = False
        book.availability = book.reserved_date + datetime.timedelta(days=14)
    else:
        book.available = False
        book.availability = book.real_availability
        
    book.save()
    
    # Redirigir a la página de descripción del libro actualizado
    return HttpResponseRedirect(reverse('book_details', args=(book_id,)))

def add_book(request):
    cancel_reservation_automatic(request)
    check_rented(request)
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            book_id = book.id
            return redirect('edit_book',book_id) 

    else:
        form = LibroForm()
    
    return render(request, 'form.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el nuevo usuario en la base de datos
            return redirect('edit_user')  # Redirigir a la página de edición de usuarios
    else:
        form = RegisterForm()
    return render(request, 'register_users.html', {'form': form})

def edit_user(request):
    # Obtén todos los usuarios de la base de datos
    users = User.objects.all()

    # Pasa los usuarios al contexto de renderizado
    return render(request, 'edit_users.html', {'users': users})

def delete_user(request):
    users = User.objects.all()
    return render(request, 'delete_users.html', {'users': users})

def eliminar_usuario(request, user_id):

    user = get_object_or_404(User, id=user_id)
    
    print('eliminando el usuario')
    user.delete()
        # Redirige a la misma página después de eliminar el usuario
    return redirect('edit_user')

       

def editar_usuario(request, user_id):
    # Obtener el usuario a editar
    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Rellenar el formulario con los datos enviados en la solicitud POST
        formulario = UserForm(request.POST, instance=usuario)
        if formulario.is_valid():
            # Guardar los cambios si el formulario es válido
            usuario = formulario.save(commit=False)  # Obtener el usuario pero no guardar en la base de datos todavía
            password = formulario.cleaned_data.get('password')  # Obtener la contraseña del formulario
            if password:
                usuario.set_password(password)  # Establecer la nueva contraseña
            usuario.save()  # Guardar el usuario con los cambios
            # Redirigir a la vista de edición de usuarios 
            return redirect('edit_user')
    else:
        # Si la solicitud no es POST, mostrar el formulario con los datos del usuario
        formulario = UserForm(instance=usuario)

    # Renderizar el template 'editar_usuario.html' con el formulario y el usuario
    return render(request, 'editar_usuario.html', {'formulario': formulario, 'usuario': usuario})



def cancel_reservation_automatic(request):
    expired_reservations = Book.objects.filter(reserved=True, reserved_date__lt=date.today())
    for book in expired_reservations:
        book.reserved = False
        book.reserved_date = None
        book.reserved_by = None
        book.save()
        
        


# def rent_book(request, book_id):
#     book = get_object_or_404(Book, pk=book_id)
    
#     if book.real_available:
#         book.real_available = False
#         book.real_availability = datetime.date.today() + datetime.timedelta(days=14)
#         book.availability = datetime.date.today() + datetime.timedelta(days=14)
#     else:
#         book.real_available = True
#         book.availability = None
#         book.available = True
#         book.reserved = False
    
#     book.save()
    
#     return HttpResponseRedirect(reverse('book_details', args=(book_id,)))
        

def check_rented(request):
    today = timezone.now().date()  # Asegurarse de que la fecha es consciente de la zona horaria
    book_list = Book.objects.filter(real_availability__lt=today)
    for book in book_list:
        book.real_availability = None
        book.save()


def book_history(request):
    actual_user = BookHistory.objects.get(user_id=request.user.id)
    book_history = BookHistory.objects.get(user = request.user)
    user = book_history.user

    return render(request, 'book_history.html',{'book_history':book_history, 'user':user})


@staff_member_required
def rent_name(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username=username).first()
        if user:
            book_history = BookHistory.objects.get(user = user)
        else:
            book_history = BookHistory()

        show_message_box = False
        show_message_box2 = False
        

        if not user:
            messages.error(request, "User does not exist.")
            return render(request, 'rent_name.html', {'book': book})

        if book.reserved:
            # messages.error(request, "b reserved")
            # return render(request, 'rent_name.html', {'book': book})
            if book.reserved_by == user:
                book.reserved = False
                book.reserved_by = None
                book.reserved_date = None
                book.real_available = False
                book.real_availability = timezone.now() + datetime.timedelta(days=14)
                book.availability = timezone.now() + datetime.timedelta(days=14)
                book.rented_by = user
                book.save()
                book_history.rented_books.add(book)
                book_history.save()
                message = f"The book was successfully rented to {username} until {book.real_availability}."
                return render(request, 'rent_name.html', {'book': book, 'message': message, 'show_message_box2': True, 'username': username})
            else:
                message = f"This book is currently reserved by {book.reserved_by.username} until {book.reserved_date}. Do you want to rent it to {username}?"
                return render(request, 'rent_name.html', {'book': book, 'message': message, 'show_message_box': True, 'username': username})
        else:
            book.reserved = False
            book.reserved_by = None
            book.reserved_date = None
            book.real_available = False
            book.real_availability = timezone.now() + datetime.timedelta(days=14)
            book.availability = timezone.now() + datetime.timedelta(days=14)
            book.rented_by = user

            book.save()
            book_history.rented_books.add(book)
            book_history.save()
            message = f"The book was successfully rented to {username} until {book.real_availability}."
            return render(request, 'rent_name.html', {'book': book, 'message': message, 'show_message_box2': True, 'username': username})
    return render(request, 'rent_name.html', {'book': book})
            
            
# @staff_member_required
# def confirm_rental(request, book_id, username):
#     book = get_object_or_404(Book, pk=book_id)
#     book_history = BookHistory.objects.get(user = user)
#     show_message_box2 = False
    
#     user = User.objects.filter(username=username).first()
#     book.reserved = False
#     book.reserved_by = None
#     book.reserved_date = None
#     book.real_available = False
#     book.real_availability = timezone.now() + datetime.timedelta(days=14)
#     book.availability = timezone.now() + datetime.timedelta(days=14)
#     book.save()
#     book_history.rented_books.add(book)
#     book_history.save()
    
#     message = f"The book was successfully rented to {username} until {book.real_availability}."
#     return render(request, 'rent_name.html', {'book': book, 'message': message, 'show_message_box2': True, 'username': username})

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from .models import Book, BookHistory

@staff_member_required
def confirm_rental(request, book_id, username):
    book = get_object_or_404(Book, pk=book_id)
    user = get_object_or_404(User, username=username)
    
    try:
        book_history = BookHistory.objects.get(user=user)
    except BookHistory.DoesNotExist:
        # Maneja el caso en el que no existe un BookHistory para el usuario
        book_history = BookHistory.objects.create(user=user)
    
    book.reserved = False
    book.reserved_by = None
    book.reserved_date = None
    book.real_available = False
    book.real_availability = timezone.now() + datetime.timedelta(days=14)
    book.availability = timezone.now() + datetime.timedelta(days=14)
    book.save()
    
    book_history.rented_books.add(book)
    book_history.save()
    
    message = f"The book was successfully rented to {username} until {book.real_availability}."
    return render(request, 'rent_name.html', {'book': book, 'message': message, 'show_message_box2': True, 'username': username})



@staff_member_required
def cancel_rent(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    book.real_available = True
    book.real_availability = None
    book.availability = None
    book.available = True
    book.reserved = False
    book.reserved_by = None
    book.reserved_date = None
    book.save()
    return redirect('book_description', book_id=book_id)

def edit_book(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)
    details = BookDetails.objects.get(book = book)
    
    if request.method == 'POST':
        form_book = LibroForm(request.POST, request.FILES, instance=book)
        form_details = DetailsForm(request.POST, instance=details)

        if form_book.is_valid() and form_details.is_valid():

            form_book.save()
            form_details.save()
            return redirect('book_description', book_id=book_id)
    else:
        form_book = LibroForm()
        form_details = DetailsForm()
    
    return render(request, 'edit_book.html', {'form_book': form_book,'form_details': form_details,'book':book,'bookdetails':details})


def delete_book(request, book_id):
    cancel_reservation_automatic(request)
    check_rented(request)
    book = get_object_or_404(Book, pk=book_id)

    book.delete()
            
    return redirect('home')