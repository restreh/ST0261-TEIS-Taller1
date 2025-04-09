# library/interfaces.py
from abc import ABC, abstractmethod

class LibraryInterface(ABC):

    @abstractmethod
    def cancel_reservation_automatic(self):
        pass

    @abstractmethod
    def check_rented(self):
        pass
