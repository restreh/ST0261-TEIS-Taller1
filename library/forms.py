
from django import forms
from .models import Book, BookDetails

class LibroForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'image', 'reserved_date', 'reserved','rating_average']

class DetailsForm(forms.ModelForm):
    class Meta:
        model = BookDetails
        fields = ['isbn', 'publisher', 'genre', 'subject']
