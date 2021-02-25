"""
MIT License

Copyright (c) 2017-2018 Anselm Kiefner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from collections import Counter, OrderedDict, defaultdict
from copy import copy
from functools import wraps
from inspect import isclass
from logging import INFO, basicConfig, getLogger
from uuid import UUID, uuid4
from warnings import warn

import q

logger = getLogger("fluxx")
logger.setLevel(INFO)

FORMAT = "%(message)s"
basicConfig(format=FORMAT)


class FluxException(RuntimeWarning):
    pass


class TraitBag:
    __slots__ = ["__weakref__", "traits", "bag", "name"]

    def __init__(self, name=None, *, in_traits=(), stereotypes=(), ex_traits=(), bag=()):
        """First set up stereotypes of traits as sets of Enum seperate from the class
        and add all the traits that should be included in a "class" of TraitBags.
        Pass in those stereotypes and polish the rough edges by taking
        away the traits that should be excluded and add ones that aren't included in stereotypes.

        You really DO NOT want to subclass this.
        The point of TraitBag is that they only represent state, nothing more.
        Even more so, __slots__ don't play nice with subclassing
        (a subclass creates its own dict, killing the whole point of __slots__), so, if you NEED
        a TraitBag with methods, use the TraitMixin for instance with StateMachine
        (the TraitMachine takes a different approach all together).

        The bag is used with tokens (another Enum) for most simple use cases.
        If there's a need to extend a "class" of TraitBags, don't do it here.
        Instead, use some "global" WeakKeyDictionary or WeakValueDictionary to manage things.
        Keep in mind that in this case you will probably need one to
        map from name to thing and then from thing to property.. and be VERY CAREFUL when you
        use more than one strong ref to the thing - otherwise the weakrefs WILL bite your butt!

        One more thing: the point of TraitBag.clone() is to be able to prototype.
        You can build one complex prototype of a TraitBag, then replicate
        the bugger without any of the boilerplate.
        Careful bout those global dicts though - the clone needs extra love.
        """
        self.name = uuid4() if name is None else name
        self.bag = Counter(bag)
        # unpack the list of stereotypes and sets of traits, yielding all traits
        # but since it's a SET-comprehension, return a set of traits
        self.traits = {t for S in stereotypes for t in S}
        self.traits.update(set(in_traits))
        self.traits.difference_update(set(ex_traits))

    def __str__(self):
        return str(self.name) if not isinstance(self.name, UUID) else self.name.hex[:5]

    def __eq__(self, other):
        return self.traits == other.traits and self.bag == other.bag

    def __repr__(self):
        return f"TraitBag(name={self.name}, in_traits={self.traits}, bag={self.bag})"

    def clone(self, name=None):
        c = copy(self)
        c.name = uuid4() if name is None else name
        return c


class StateMachine:
    """Most general freaking FSM.

    If you can think of anything that has discrete states, you can probably
    model it with this. You can register callback functions to when the
    SM changes state. In case you want to have dynamic methods, you need to
    implement a kind of dispatch mechanism. This is what the accept method is for -
    taking requests and dispatching them to other methods.

    It is also possible to work with State classes instead of Enums,
    but to keep things concise, you should try to work with reg_enter etc. instead
    of implementing enter() methods. Classes have the advantage that you can
    have state-dependent @staticmethods so that you can just call a common interface
    without worrying about dispatching.

    enters, exits are dicts of state to function that needs to be called on event.
    transitions is a dict of (state, state) that is called in transition of exactly those two states,
    thus more specific than enters or exits.
    """

    def __init__(
        self,
        *,
        states: dict,
        initial,
        name=None,
        enters=None,
        exits=None,
        transitions=None,
        history=None,
        tracing=False,
        bag=None,
    ):
        self.name = uuid4() if name is None else name
        self.bag = Counter()
        if bag is not None:
            self.bag.update(bag)

        self.states = {}
        self.states.update(states)
        self.state = initial
        self.previous = initial

        self.transitions = defaultdict(lambda: lambda: None)
        if transitions is not None:
            self.transitions.update(transitions)

        self.enters = defaultdict(lambda: lambda: None)
        if enters is not None:
            self.enters.update(enters)

        self.exits = defaultdict(lambda: lambda: None)
        if exits is not None:
            self.exits.update(exits)

        if tracing:
            self.history = [initial] if history is None else history
        self.tracing = tracing

    def accept(self, aim, *args):
        """
        Prototype for a dispatch mechanic. Should be overwritten in subclasses.

        In summary:
        Since a caller shouldn't worry (especially if async) about the state we are in,
        they make an educated guess what we can do and make a request in form of passing
        a token Enum with optional args.

        We don't expose our functions but instead dispatch the token here - see if we are in a state
        that can accept the token and if so, to which function it should go.

        It is important to maintain a consistent interface.
        Usually this means only returning True or False, but if we need to chain such requests,
        message passing (for instance a namedtuple or dictionary as result) is recommended.

        This might require either passing a callback (cb) and errback (eb) function or
        the instance of the actor.
        """
        raise NotImplementedError

    def flux_to(self, to_state):
        try:
            if to_state in self.states[self.state]:
                # Exceptions aren't caught here because this might result in undefined behaviour
                # crash early - crash often
                self.exits[self.state]()
                self.transitions[(self.state, to_state)]()
                self.enters[to_state]()

                self.previous = self.state  # often used in user code
                self.state = to_state
                if isclass(to_state):
                    q(f"{self.name} now {to_state.__name__}")
                else:
                    q(f"{self.name} now {to_state}")
                if self.tracing:
                    self.history.append(to_state)
                return True
            else:
                warn(f"no valid transition from {self.state} to {to_state}", UserWarning)
                return False
        except KeyError:
            warn(f"{self.state} is final", UserWarning)
            return False

    @property
    def next_possible_states(self):
        try:
            return self.states[self.state]
        except KeyError:
            return set()

    def reg_enter(self, *args):
        """Register a function that is called when a state is entered.
        Can be used with a lambda or as decorator.
        like
        >>> sm = StateMachine(...)
        >>> @sm.reg_enter(S.foo)
        >>> def do_stuff_on_entry(self, e):
            ...
        or
        >>> sm.reg_enter(S.foo, lambda e: ...)
        """
        if len(args) == 2:
            state, func = args
            self.enters[state] = func
        if len(args) == 1:
            state = args[0]

            def decorator(func):
                self.enters[state] = func

            return decorator

    def reg_exit(self, *args):
        """Register a function that is called when a state is exited.
        Can be used with a lambda or as decorator.
        """
        if len(args) == 2:
            state, func = args
            self.exits[state] = func
        if len(args) == 1:
            state = args[0]

            def decorator(func):
                self.exits[state] = func

            return decorator

    def reg_transit(self, *args):
        """Register a function that is called during transit from one specific state to another.
        Can be used with a lambda or as decorator.
        """
        print(args, len(args))
        if len(args) == 3:
            self.transitions[(args[0], args[1])] = args[2]
        if len(args) == 2:
            from_state, to_state = args

            def decorator(func):
                self.transitions[(from_state, to_state)] = func

            return decorator

    def clone(self, name=None):
        c = copy(self)
        c.name = uuid4() if name is None else name

        c.states = {}
        c.states.update(self.states)

        c.transitions = defaultdict(lambda: lambda e: None)
        c.transitions.update(self.transitions)

        c.enters = defaultdict(lambda: lambda e: None)
        c.enters.update(self.enters)

        c.exits = defaultdict(lambda: lambda e: None)
        c.exits.update(self.exits)
        return c

    def __str__(self):
        return str(self.name) if not isinstance(self.name, UUID) else self.name.hex[:5]

    def __repr__(self):
        return f"{self.name} in {self.state} with {self.states}"

    def __mul__(self, number):
        for x in range(number):
            yield self.clone()

    def __call__(self):
        """This makes it possible to easily realize hierarchical statemachines with Collector
        by assuming that each FSM can be called to return its current state and applying
        the composition pattern.
        This means we have a recursive structure of Collectors and StateMachines
        being the leaves of the call tree.
        """
        return self.state


class Collector(StateMachine):
    """Quite sophisticated Super-StateMachine.
    It can be used with anything that can be called, returning a valid state enum,
    including TraitMachines.

    Conditions are tricky. It's an ordered dictionary of frozensets of tuples
    (machine, state) which points to a state. It's more convenient to just use
    c = Collector(...)
    m = StateMachine(...)
    c[(m, s1)] = s2

    Much easier that way and less error prone. The conditions are evaluated in
    reversed order, so if you insist on some priority,
    just make sure to add the more specific condition after the more general.
    """

    def __init__(
        self, *, states: dict, conditions=None, initial, name=None, default=None, **kwargs
    ):
        super().__init__(states=states, initial=initial, name=name, **kwargs)

        self.conditions = OrderedDict()
        if conditions is not None:
            self.conditions.update(conditions)

        self.default = initial if default is None else default

    def __setitem__(self, key, value):
        try:
            m, s = key
            if isinstance(m, StateMachine):
                key = [key]
        except ValueError:
            pass
        self.conditions[frozenset(key)] = value
        self.recursion_check(self.conditions.keys())

    def recursion_check(self, conditions):
        # conditions = [frozenset((fsm, state),)]
        for c in conditions:
            for sm, s in c:
                if sm is self:
                    raise FluxException("Collector contains itself by recursion!")
                else:
                    if isinstance(sm, Collector):
                        self.recursion_check(sm.conditions.keys())

    def __delitem__(self, key):
        if isinstance(key, tuple):
            key = [key]
        del self.conditions[frozenset(key)]

    def __call__(self):
        # since self.conditions is ordered, execution is not arbitrary
        for c, t_state in reversed(self.conditions.items()):
            if all(sm() is s for sm, s in c):
                self.flux_to(t_state)
                break
        # else is only executed if loop is completed
        else:
            self.flux_to(self.default)
        return self.state

    def clone(self, name=None):
        # better alternative would be to implement __repr__ correctly,
        # then instantiate a new machine from that repr.
        # However, that would require pickling recursive functions, which is non-trivial.

        new = copy(self)
        new.name = uuid4() if name is None else name

        new.states = {}
        new.states.update(self.states)

        new.transitions = defaultdict(lambda: lambda e: None)
        new.transitions.update(self.transitions)

        new.enters = defaultdict(lambda: lambda e: None)
        new.enters.update(self.enters)

        new.exits = defaultdict(lambda: lambda e: None)
        new.exits.update(self.exits)

        new.conditions = {}
        new.conditions.update(self.conditions)
        return new


class TraitMixin:
    """Use this in connection with another class get the benefit of a TraitBag
    without strings attached.

    >>> class Door(TraitMixin, StateMachine):
    >>>    pass
    """

    def __init__(self, *, in_traits=(), stereotypes=(), ex_traits=(), **kwargs):
        super().__init__(**kwargs)
        # unpack the list of stereotypes and sets of traits, yielding all traits
        # but since it's a SET-comprehension, return a set of traits
        self.traits = {t for S in stereotypes for t in S}
        self.traits.update(set(in_traits))
        self.traits.difference_update(set(ex_traits))


class TraitMachine(StateMachine):
    """The state machine paradigm taken the other way round.

    A statemachine whose state depends on its traits, compatible to Collector.
    You add or remove traits, which may flux its state when evaluated.

    This is particularly useful if you have a lot of moving parts and the luxury to postpone evaluation for a while
    like in an event loop.
    """

    def __init__(
        self,
        *,
        initial,
        default=None,
        stereotypes=None,
        in_traits=None,
        ex_traits=None,
        trait_states=None,
        **kwargs,
    ):
        super().__init__(initial=initial, **kwargs)

        self.default = default

        stereotypes = [] if stereotypes is None else stereotypes
        in_traits = set() if in_traits is None else in_traits
        ex_traits = set() if ex_traits is None else ex_traits

        self.traits = {t for S in stereotypes for t in S}
        self.traits.update(set(in_traits))
        self.traits.difference_update(set(ex_traits))

        self.trait_states = {} if trait_states is None else trait_states

    def __call__(self):
        try:
            to_state = self.trait_states[frozenset(self.traits)]
            if to_state is not self.state:
                self.flux_to(to_state)
        except KeyError:
            if self.default is not None:
                self.flux_to(self.default)
        return self.state


class TraitStateMachine(StateMachine):
    """Pretty badass alternative to local dispatching.

    We define by set operations over enums which methods should be available
    for any given state. It doesn't matter where the methods are defined
    (as long as it's not the same class, that would make things messy again) and we don't care
    about special dispatch logic because we decorate the functions with @can() to specify
    which Trait a thing should have to make the function applicable.
    This kills two birds with one stone: All the important logic is in one place -
    the instantiation call for the TraitMachine - and functions can be implemented anywhere,
    as long as they adhere to the convention with can()-decorator and taking thing as main arg.
    """

    def __init__(
        self,
        *,
        initial,
        stereotypes=None,
        in_traits=None,
        ex_traits=None,
        stateful_traits=None,
        **kwargs,
    ):
        super().__init__(initial=initial, **kwargs)

        stereotypes = [] if stereotypes is None else stereotypes
        in_traits = set() if in_traits is None else in_traits
        ex_traits = set() if ex_traits is None else ex_traits

        self.stateless_traits = {t for S in stereotypes for t in S}
        self.stateless_traits.update(set(in_traits))
        self.stateless_traits.difference_update(set(ex_traits))

        self.stateful_traits = defaultdict(lambda: set())
        if stateful_traits is not None:
            self.stateful_traits.update(stateful_traits)

        self.traits = self.stateless_traits | self.stateful_traits[self.state]

    def __call__(self):
        self.traits = self.stateless_traits | self.stateful_traits[self.state]
        return self.state

    def flux_to(self, to_state):
        w = super().flux_to(to_state)
        self.traits = self.stateless_traits | self.stateful_traits[self.state]
        return w


def can(in_trait, ex_trait=None, observed=None):
    """Decorator for "case-dispatch" via logical set operations on traits
    (which can be any kind of singleton like enums).

    If something should be able to call something, you give it a token aka trait.

    In case you want to check for any number of traits, this decorator
    could easily be modified to take sets.
    """

    def wrapper(func):
        # Delegation of different wrappers for methods and standalone functions under the same umbrella.
        # Also faster to do the check first and delegate to the correct function based on case than to check the case every call during runtime.

        # first we check if we've been given a thing to observe initially
        if observed:

            @wraps(func)
            def calling(*args, **kwargs):
                if in_trait in observed.traits and not ex_trait in observed.traits:
                    func(*args, **kwargs)
                else:
                    try:
                        warn(
                            f"{func.__qualname__} isn't available while {observed.name} {observed.state} (called with {args} {kwargs})"
                        )
                    except AttributeError:
                        warn(
                            f"{func.__qualname__} can't be called, {observed} has no {in_trait}"
                        )

        # next we might have a class method
        elif len(func.__qualname__.split(".")) > 1:

            @wraps(func)
            def calling(*args, **kwargs):
                self, thing, *_ = args
                if in_trait in thing.traits and not ex_trait in thing.traits:
                    func(*args, **kwargs)
                else:
                    try:
                        warn(
                            f"{func.__qualname__} isn't available while {thing.name} {thing.state} (called with {args} {kwargs})"
                        )
                    except AttributeError:
                        warn(
                            f"{func.__qualname__} can't be called, {thing} has no {in_trait}"
                        )

        # leaves us with a module-level function
        else:

            @wraps(func)
            def calling(*args, **kwargs):
                thing, *_ = args
                if in_trait in thing.traits and not ex_trait in thing.traits:
                    func(*args, **kwargs)
                else:
                    try:
                        warn(
                            f"{func.__qualname__} isn't available while {thing.name} in {thing.state} (called with {args} {kwargs})"
                        )
                    except AttributeError:
                        warn(
                            f"{func.__qualname__} can't be called, {thing} has no {in_trait}"
                        )

        return calling

    return wrapper
