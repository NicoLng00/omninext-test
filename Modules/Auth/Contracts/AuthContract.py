from abc import ABC, abstractmethod

class AuthContract(ABC):
    
    @abstractmethod
    def login(self, email, password):
        """Authenticate a user with email and password"""
        pass
    
    @abstractmethod
    def register(self, user_data):
        """Register a new user"""
        pass