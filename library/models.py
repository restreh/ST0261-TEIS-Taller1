from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField(default='Description not available')
    image = models.ImageField(upload_to='library/images/')
    available = models.BooleanField(default=True)
    availability = models.DateField(null=True, blank=True)
    real_available = models.BooleanField(default=True)
    real_availability = models.DateField(null=True, blank=True)
    reserved = models.BooleanField(default=False)
    reserved_date = models.DateField(null=True, blank=True)
    reserved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='books_reserved'
    )
    rented_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='books_rented'
    )
    total_ratings = models.IntegerField(default=0)
    sum_ratings = models.IntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)

class BookDetails(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='bookdetails', default=None)
    isbn = models.CharField(max_length=13,default='N/A')
    genre = models.CharField(max_length=100,default='N/A')
    subject = models.CharField(max_length=100, default='N/A')
    publisher = models.CharField(max_length=100, default='N/A')

#Esta función crea automáticamente un objeto de BookHistory asociado cuando se crea un nuevo usuario.
def create_bookdetails_book(sender, instance, created, **kwargs):

    if created:
         BookDetails.objects.create(book=instance)

#Esta función guarda automáticamente el historial de libros después de que se guarda el objeto User.
def save_bookdetails_book(sender, instance, **kwargs): 
    instance.bookdetails.save()

post_save.connect(create_bookdetails_book, sender=Book)
post_save.connect(save_bookdetails_book, sender=Book)

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Hacer el campo anulable
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    value = models.IntegerField()

    class Meta:
        unique_together = ('book', 'user')

class BookHistory(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bookhistory', default=None)
    rented_books = models.ManyToManyField(Book, blank=True)

#Esta función crea automáticamente un objeto de BookHistory asociado cuando se crea un nuevo usuario.
def create_bookhistory_user(sender, instance, created, **kwargs):

    if created:
         BookHistory.objects.create(user=instance)

#Esta función guarda automáticamente el historial de libros después de que se guarda el objeto User.
def save_bookhistory_user(sender, instance, **kwargs): 
    instance.bookhistory.save()

# Estas 2 líneas de código conectan las funciones a las señales post_save para el modelo User.
# Cuando se crea o actualiza un objeto User, estas funciones se ejecutan automáticamente.

post_save.connect(create_bookhistory_user, sender=User)
post_save.connect(save_bookhistory_user, sender=User)