'''
Created on Mar 8,2015
@author: qiuyx
'''
from abc import abstractmethod, ABCMeta

class Command(object):
    __metaclass__ = ABCMeta
    """Base class for all commands."""
    
    @abstractmethod
    def genXML(self):
        """:return: XML representation of the command."""
        pass

    @abstractmethod
    def __repr__(self):
        """:return: Representation that can be used to create the command in python."""
        return "Command()"

    def __str__(self):
        """By default, calls `__repr__()`.
        :return: Concise, human-readable representation.
        """
        return self.__repr__()

    def indent(self, level):
        return "    " * level
    
    def format(self, level=0):
        """Format the command, possible over multiple lines.
        
        :param level: Indentation level
        
        :return: Human-readable, possibly multi-line representation.
        """
        return self.indent(level) + self.__str__()
