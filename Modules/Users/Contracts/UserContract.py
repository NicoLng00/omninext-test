from abc import ABC, abstractmethod



class UserContract(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str):
        pass



