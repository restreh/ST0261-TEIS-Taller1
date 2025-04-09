# library/services.py
from datetime import date
from django.utils import timezone
from .models import Book
from .library_interfaces import LibraryInterface

class LibraryService(LibraryInterface):

    def cancel_reservation_automatic(self):
        expired_reservations = Book.objects.filter(reserved=True, reserved_date__lt=date.today())
        for book in expired_reservations:
            book.reserved = False
            book.reserved_date = None
            book.reserved_by = None
            book.save()

    def check_rented(self):
        today = timezone.now().date()
        book_list = Book.objects.filter(real_availability__lt=today)
        for book in book_list:
            book.real_availability = None
            book.save()
