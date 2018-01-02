'''
Created on Nov 26, 2017

@author: Salim
'''
from abc import ABCMeta, abstractmethod
from enum import Enum
from _pyio import __metaclass__
from io import IOBase
import types
from io import BytesIO
from umsgpack import UnsupportedTypeException
    
    
    
class Deserializer():
    '''
        Base Deserializer class. It only specifies that it needs a handled_class method
    '''
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def execute(self, events, pdict, count):
        raise Exception('Not implemented');
    
    
    

class EventBasedDeserializer(Deserializer):
    '''
        EventBasedDeserializer will execute deserializer over an iterator over events corresponding to the given object
    '''
    __metaclass__ = ABCMeta
    
    def execute(self, events, pdict, count):
        tmp = EventStream(ClassEventIterator(events,pdict, count))
        val = self.deserialize(tmp, pdict)
        try:
            while tmp.next():
                pass
        except StopIteration:
            pass
            
        return val
            
    
    @abstractmethod
    def deserialize(self, events, pdict):
        raise Exception('Not implemented');
    
    
class ClassEventIterator(object):
    
    def __init__(self, events,pdict, count=0):
        self._events = events
        self._count = count
        self._pdict = pdict
        self._isdone = False
        if self._count == 0:
            if  self._pdict.is_obj_start(events.next()):
                self._count = self._count + 1
            else:
                raise Exception("Expected a object start event but didn't receive one")
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._isdone:
            raise StopIteration()
        event = self._events.next()
        if event:
            if self._pdict.is_obj_start(event):
                self._count = self._count + 1
            elif self._pdict.is_obj_end(event):
                self._count = self._count - 1
                if self._count == 0:
                    self._isdone = True
                    return None
            return event
        else:
            return event
        
        

    next = __next__  # Python 2
    



        
        
    
class POPState(Enum):
    
    EXPECTING_OBJ_START = 1
    EXPECTING_OBJ_PROPERTY_OR_END = 3
    EXPECTING_VALUE = 4
    EXPECTING_ARRAY_START = 5
    EXPECTING_VALUE_OR_ARRAY_END = 6
    


class Typed():
    '''
        Basic class for classes that will support typed object based serialization. 
        Extending this class is not required to support type resolution however, 
        it will make the code cleaner
    '''
    
    _types = {}
        
        
    @classmethod
    def resolve(cls, propname, objcls=None):
        '''
            resolve type of the class property for the class. If objcls is not set then 
            assume that cls argument (class that the function is called from) is the class 
            we are trying to resolve the type for 
        :param cls:
        :param objcls:
        :param propname:
        '''
        # object class is not given
        if objcls is None:
            objcls = cls
        # get type
        typemap = cls._types.get(objcls)
        if(typemap is not None):
            # nothing registered for this property
            return typemap.get(propname, None)
        # type map didn't exist so none
        return None
    
    @classmethod
    def register_type(cls, propname, valcls, objcls=None):
        '''
            register type for class 
             
        :param cls:
        :param propname:
        :param valcls:
        :param objcls:
        '''
        # object class is not given
        if objcls is None:
            objcls = cls
        # get type map for objcls
        typemap = cls._types.get(objcls, None)
        # if type map doesn't exist then remove it
        if not typemap:
            typemap = {}
            cls._types[objcls] = typemap
        # register value class for property
        typemap[propname] = valcls
        
        





class Parser():
    '''
        Used for parsing to events
    '''
    
    __slots__ = ['_pdict']
    
    
    def __init__(self, pdict):
        self._pdict = pdict
        
        
    
    def parse(self, data):
        
        
        if type(data) is types.StringType:
            data = BytesIO(data);
            data.seek(0)
        if type(data) is types.FileType:
            pass
        elif isinstance(data, IOBase):
            pass
        else:
            raise UnsupportedTypeException('input should be of one the types [str, IOBase, file] but ' + str(type(data)) + " was received!!")
        
        return self._gen_events(data)
        
    def _gen_events(self, instream):
        '''
            generates events using the specific parser
        :param instream:
        '''
        return EventStream(self._pdict.gen_events(instream))
        
    
class EventStream():
    '''
        Wrapper Iterator as output of Parser
    '''
    
    def __init__(self, events):
        self._events = events
        
    
    def __iter__(self):
        return self

    def __next__(self):
        return  self._events.next()
    
    next = __next__  # Python 2
    
    


