"""
URL configuration for libraryproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from library import views as library_views
from library.views import *

from django.conf.urls.static import static
from django.conf import settings

from library import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', library_views.home, name='home'),
    path('about/', library_views.about),
    path('book_description/<int:book_id>/', book_details, name='book_description'),
    path('book_details/<int:book_id>/', book_details, name='book_details'),  # Nueva URL para book_details
    path('change_availability/<int:book_id>/', views.change_availability, name='change_availability'),
    path('reserve_book/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('change_real_availability/<int:book_id>/', views.change_real_availability, name='change_real_availability'),
    path('verify_availability/<int:book_id>/', views.verify_availability, name='verify_availability'),
    path('adminrent/<int:book_id>/', views.adminrent, name='adminrent'),
    path('rate-book/', views.rate_book, name='rate_book'),
    path('submit_review/', views.submit_review, name='submit_review'),
    path('form/', views.add_book, name='add_book'),
    path('mainapp/', include('mainapp.urls')),
    path('book_history/', views.book_history, name='book_history'),
    path('rent_name/<int:book_id>/', library_views.rent_name, name='rent_name'),  # URL para procesar el alquiler del libro
    path('book_description/<int:book_id>/<str:username>/', views.confirm_rental, name='confirm_rental'),
    path('cancel_rent/<int:book_id>/', views.cancel_rent, name='cancel_rent'),
    path('register_users/', views.register_user, name='register_user'),
    path('edit_users/', views.edit_user, name='edit_user'),
    path('editar_usuario/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('delete_users/', views.delete_user, name='delete_user'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


