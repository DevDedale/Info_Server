"""
These are the most importants objects on which the Magichanism framework is based.
"""
import itertools
import sys
import logging
import traceback
import time
from misc.meta import InstanceFactory, InstanceFactoryProduct
import stackprinter
from threading import Lock

class BaseState(InstanceFactoryProduct):
    """
    This is the base class of almost all the GameServer internals logics.
    A BaseState represents a value which may be used, updated displayed...
    It is possible to register callbacks to be notified on value update
    """

    def __init__(self, logic):
        self.value = None
        self.logic = logic
        self.callbacks_lock = Lock()
        self.on_state_change_callbacks = {}
        self.debug = False
        self.uid = self.new_uid()

    def set_debug(self, status):
        self.debug = status

    def new_uid(self):
        """generate a unique UID to identify the state"""

        return self.logic.new_uid(self.__class__.__name__)

    def check_value(self, value):
        """
        This function may be overloaded to check if the value setted is valid
        """
        return True

    def set(self, v):
        """Update the state value"""
        if self.check_value(v):
            return self.update_value(v)
        else:
            raise RuntimeError('Invalid value for state %s (%s)'%(self,v))

    def get(self):
        """Get the current state value"""

        return self.value

    def setter(self, v):
        """ meta programming helper to get a closure which will set state value to v """
        def _set_closure():
            self.set(v)
        return _set_closure

    def mutator(self, f):
        """ meta programming helper to get a closure which will apply f to state value """
        def _f_closure(*args):
            self.set(f(self.get(), *args))
        return _f_closure

    def on_change(self, f, call_immediately=False, args=()):
        """
        Register a callback to be notified on value changes, if
        call_immediately is True callback will be immediately called on
        subscription
        """

        if f is None:
            raise Exception('Callback is None')
        with self.callbacks_lock:
            self.on_state_change_callbacks[f] = args

        if call_immediately:
            self.call_state_changed_callback(f, self.value, None, args)

        return self

    def is_on_change_registered(self, f):
        with self.callbacks_lock:
            return f in self.on_state_change_callbacks

    def on_change_remove(self,f):
        if not self.is_on_change_registered(f):
            raise Exception('Unknown callback')

        with self.callbacks_lock:
            self.on_state_change_callbacks.pop(f)

    def on_change_clear(self):
        with self.callbacks_lock:
            self.on_state_change_callbacks = {}

    def emit_logic_on_state_change(self):
        self.logic.events.emit("state_changed", None, self)

    def call_state_changed_callback(self, cb, new, old, args):
        if len(args) > 0:
            cb(new, old, self, *args)
        else:
            cb(new)


    def call_state_changed_callbacks(self, new, old):
        """Call safely all registered callbacks with the new value"""

        self.emit_logic_on_state_change()

        # copy callbacks to avoid concurrent modification
        items = {}
        with self.callbacks_lock:
            items = self.on_state_change_callbacks.copy().items()
        
        for cb, args in items:
            try:
                self.call_state_changed_callback(cb, new, old, args)
            except Exception as e:
                etype, evalue, etb = sys.exc_info()
                logging.error("Exception %s in state callback: %s"%(etype.__name__,evalue))
                for filename,line,function,text in traceback.extract_tb(etb):
                    logging.error(" - in file %s:%d, in %s : %s"%(
                        filename,line,function,text))

        if self.debug:
            msg=stackprinter.format(show_vals=False, style='darkbg2')
            logging.info('STATE CHANGED %s: %s'%(self.get_state_serialized(), msg))

    def update_value(self, new, force=False):
        """
        Update the state value with the new one.
        Returns True if it was actually changed
        """
        updated = force or (new != self.value)
        old = self.value
        self.value = new
        if updated:
            self.call_state_changed_callbacks(new, old)
            return True
        return False

    def get_state_serialized(self):
        return {
            'uid': self.uid,
            'value': self.value
        }

class State(BaseState):
    """
    A state which validity is shared with other states through is parent.
    This allow for exemple, to invalidate a series of states
    when its device gets offline
    """

    def __init__(self, logic, parent):
        """
        Constructor
        
        :param parent: parent Container object
        """
        BaseState.__init__(self, logic)
        self.parent = parent

        validity_state = self.get_validity_state()

        if validity_state is not None:
            # register callback on validity change
            def _on_validity_changed(new):
                self.call_state_changed_callbacks(self.value, new)
            validity_state.on_change(_on_validity_changed)

    def path(self):
        """ Return state full path """
        pname = str(self.__class__.__name__) if self.name is None else str(self.name)
        return '/'.join((self.parent.path(), pname))

    def emit_logic_on_state_change(self):
        self.logic.events.emit("state_changed", self.parent, self)

    def get_validity_state(self):
        """Return the state representing the value validity"""

        return self.parent.get_validity_state()

    def get_validity(self):
        """
        state validity is inherited from parent if not None, 
        always True otherwise
        """
        validity_state = self.get_validity_state()
        if validity_state is None:
            return True
        else:
            return validity_state.get()
   
    def call_if(self, f):
        """ meta programming helper which return a closure calling f only if state value is evaluated as true """
        def _f_closure(*args):
            if self.get_validity() and self.value:
                f(*args)
        return _f_closure

    def get_state_serialized(self):
        s = super().get_state_serialized()
        s['valid'] = self.get_validity()
        return s

class NamedState(State):
    """
    A NamedState is State identified by its custom name
    """

    NAME="named"

    def __init__(self, logic, parent, name):
        """
        Constructor
        
        :param parent: parent Container object
        :param name: the custom identifier name
        """

        State.__init__(self, logic, parent)
        self.name = name
        self.is_persistent = False

    def make_persistent(self, default=None):
        self.is_persistent = True

        key = self.path()

        if self.logic.database is None:
            # if no database is defined, simply set value to default
            super().set(default)
            return

        if key in self.logic.database:
            # key found in database, get stored value and set state
            try:
            	value = self.logic.database[key]
            	super().set(value)
            except Exception as e:
                self.logic.log_error("DATABASE: impossible to get initial value for %s"%key)
                self.set(default)
        else:
            # key not found in database, set default value
            self.set(default)

    def update_value(self, v, force=False):

        updated = super().update_value(v, force)

        if updated and self.is_persistent and self.logic.database is not None:
            key = self.path()
            self.logic.database[key] = v

        return updated

    def get_state_serialized(self):
        s = super().get_state_serialized();
        s['name'] = self.name
        return s
    
    def __repr__(self):
        return "<%s(%s) object>"%(
                self.__class__.__name__,
                self.name)

class AnonymousState(NamedState):
    NAME="anonymous"
    ALLOW_ANONYMOUS_BUILD = True

class ComposedState(AnonymousState):

    NAME="composed"

    def __init__(self, logic, parent, name):
        NamedState.__init__(self, logic, parent, name)

        self.map_f = None
        self.states = []

    def set(self, v):
        """ do not allow user to set internal state """
        raise RuntimeError("Call to ComposedState.set() is not allowed")

    def _compose_not_operator(self, *args):
        for arg in args:
            if arg:
                return False 
        return True

    def _compose_equals_operator(self, *args):
        if len(args) == 1:
            return True
        
        for i in range(1, len(args)):
            if args[i] != args[i-1]:
                return False
        return True

    def _compose_and_operator(self, *args):
        for arg in args:
            if arg is None:
                return
            if not arg:
                return False 
        return True

    def get_compose_function(self, f):
        if isinstance(f, str):
            functions = {
                'not': self._compose_not_operator,
                'and': self._compose_and_operator,
                'equals': self._compose_equals_operator
                }
            if f in functions:
                return functions[f]
            else:
                raise Exception("Unknown compose function '%s'. Should be one of %s or a function"%(f, list(functions.keys())))
                return None
        return f

    def map(self, states, f):

        # unregister callbacks on previously composed states
        for s in self.states:
            s.on_change_remove(self.call_map_function)

        # store compose function and composed states
        self.map_f = self.get_compose_function(f)
        self.states = states

        # register callbacks on composed states change
        for s in self.states:
            s.on_change(self.call_map_function)

        # immediately set composed value
        self.call_map_function(None)

        return self

    def invalidate(self):
        super().set(None)

    def call_map_function(self, _):
        # if compose function is not set, set internal value to None
        if self.map_f is None:
            self.invalidate()
            return

        # check composed states validity
        for s in self.states:
            if not s.get_validity():
                self.invalidate()
                return

        # fetch values, compute composed value and assign it
        super().set(
            self.map_f(
                *[s.get() for s in self.states]
            )
        )

class MergedState(AnonymousState):

    NAME="merged"

    def __init__(self, logic, parent, name):
        NamedState.__init__(self, logic, parent, name)
        self.states = {}
        super().set({})

    def set(self, v):
        """ do not allow user to set internal state """
        raise RuntimeError("Call to MergedState.set() is not allowed")

    def merge(self, states):
        # store merged states
        if not isinstance(states, dict):
            raise RuntimeError("MergedState.merge() argument states is expected to be a dictionnary")

        self.states = states

        # check states and register callbacks on merged states change
        for key,state in self.states.items():

            if not isinstance(state, State):
                raise RuntimeError("MergedState.merge() states dictionnary is expected to hold States as values")

            state.on_change(self.merge_states_update, args=(key,))

        # immediately set merged value
        self.merge_states()

        return self
    
    def merge_states_update(self, new, old, state, key):
        #update the corresponding internal value
        self.get()[key] = new if state.get_validity() else None
        # manually raise callbacks call as root dictionnary object is not changed
        self.call_state_changed_callbacks(self.value, None)

    def merge_states(self):
        # fetch values, compute composed value and assign it
        
        super().set({
            k : state.get() if state.get_validity() else None
                for k,state in self.states.items()
        })

class Container(InstanceFactory):
    """
    A state container is used to aggregate states with common properties.
    For example, all states attached to a given physical device.
    Some magic is used to make easy the creation of attached object thanks to InstanceFactory.
    """

    def __init__(self, logic, parent, name, classes):
        """
        Constructor
        
        :param logic: the GameLogic object
        :param name: the container name
        :param parent: direct parent container
        :param classes: classes to be registered in InstanceFactory
        """

        # let's do some metaprogramming to automate peripherals
        # accessors in device 
        # (allowing a nice .device().gpio() syntax in pages)
        InstanceFactory.__init__(self, classes, [logic, self])

        self.logic = logic
        self.parent = parent
        self.name = name

        self.uid = self.new_uid()

    @staticmethod
    def join_classes(*groups):
        cls = []
        for group in groups:
            if group is not None:
                cls.extend(group)
        return cls

    def new_uid(self):
        """generate a unique UID to identify the state"""
        return self.logic.new_uid(self.__class__.__name__)

    def get_validity_state(self):
        """
        Default validity is parent validity,
        default to none if there is no parent (validity will always be true)
        """
        if self.parent is None:
            return None
        else:
            return self.parent.get_validity_state()

    def debug_walk(self,n=0):
        for child in self.children():
            if isinstance(child,Container):
                print(n*" " + "-", child)
                child.debug_walk(n+2)
            else:
                print(n*" " + "|", f"{child} {child.get_validity()} {child.get()}")

    def on_new_instance_registered(self, instance):
        # nothing to do here
        pass

    def path(self):
        """ Return container full path """
        pname = str(self.__class__.__name__) if self.name is None else str(self.name)
        return '/'.join((self.parent.path(), pname)) if self.parent else pname

    def children(self, cls=None):
        """ Return first level contained objects which are instances of cls """
        return [obj for (_,obj) in self.items() if cls is None or isinstance(obj,cls)]

    def states(self):
        """ Get a flat list of states contained in every container tree """
        states = []
        for _,p in self.items():
            if isinstance(p, Container):
                states.extend(p.states())
            else:
                states.append(p)
        return states

