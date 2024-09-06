from abc import ABC, abstractmethod


class Loader(ABC):

    @abstractmethod
    def load_data(self):
        pass
