"""Touch Classes."""

from collections import deque


class _AbstractTouch(object):
    """Abstract definition of a Spikeball touch."""

    _next = None

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Abstract Touch Class."""
        self._actor = actor
        self._success = success
        self._target = target
        self._strength = strength

    @property
    def actor(self):
        """Return actor Player."""
        return self._actor

    @property
    def success(self):
        """True if the touch was successful for the actor."""
        return self._success

    @property
    def target(self):
        """Return target Player."""
        return self._player

    @property
    def strength(self):
        """Return strength of the Touch."""
        return self._player

    @classmethod
    @property
    def next(cls):
        return cls._next


class Service(_AbstractTouch):
    """Service."""

    def __init__(self, actor, success=True, target=None, strength=None,
                 is_ace=False):
        """Initialize Service."""
        self._is_ace = is_ace if success else False
        super().__init__(actor, success, target)

    @property
    def is_ace(self):
        """Determine if the serve is an ace."""
        return self._is_ace


class Defense(_AbstractTouch):
    """Defensive Return."""

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Defensive Return."""
        super().__init__(actor, success, target, strength)


class Set(_AbstractTouch):
    """Set."""

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Set."""
        super().__init__(actor, success, target, strength)


class Spike(_AbstractTouch):
    """Spike."""

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Spike."""
        super().__init__(actor, success, target, strength)


Service._next = Defense
Defense._next = Set
Set._next = Spike
Spike._next = Defense


class ActionList(object):
    """List of actions."""

    def __init__(self, p1, p2, p3, p4, *actions):
        """Instantiate an ActionList."""
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._meta = {}
        self._action_list_strings = actions
        self._action_list = ActionList.parse(p1, p2, p3, p4, actions)
        self._iterator_index = 0

    def __str__(self):
        """Return string representation of the ActionList."""
        return ", ".join(self._action_list_strings)
    
    def __iter__(self):
    	"""Return iterator object for ActionList."""
    	return self
    
    def __next__(self):
    	"""Return next action in the ActionList."""
    	if self._iterator_index >= len(self._action_list):
    		raise StopIteration
    	else:
    		self._iterator_index += 1
    		return self._action_list[self._iterator_index]
    	
    
    def __contains__(self, item):
    	"""Return True if item is contained in ActionList."""
    	return item in self._action_list
    
    def __len__(self):
    	"""Return length of ActionList."""
    	return len(self._action_list)

    @staticmethod
    def parse(p1, p2, p3, p4, *actions):
        """Parse actions into AbstractTouches."""
        output = []

        same_team = ("1", "2")
        other_team = ("3", "4")

        def pmap(player):
            out = {"1": p1, "2": p2, "3": p3, "4": p4}.get(player)
            if out is None:
                raise Exception("ERORORO")
            else:
                return out

        for point in actions:
            touch_list = []
            touch = Service

            focus = None

            action_deque = deque(point)

            def next_touch():
                return action_deque.popleft()

            def verify_action_deque_empty(error_on=False):
                if error_on:
                    if len(action_deque) == 0:
                        raise Exception("FIX THIS")
                else:
                    if len(action_deque) != 0:
                        raise Exception("FIX THIS")

            def set_focus(player):
                global focus
                global same_team
                global other_team
                
                focus = player

                if focus not in same_team:
                    if focus in other_team:
                    	same_team, other_team = other_team, same_team
                    else:
                        raise Exception("FIX THIS")

            while len(action_deque) != 0:
                if touch is Service:
                    set_focus(next_touch())
                    modifier = next_touch()
                    if modifier == "n":
                        touch_list.append(Service(pmap(focus),
                                                  success=False))
                        verify_action_deque_empty(error_on=False)
                    elif modifier == "a":
                        target = next_touch()
                        if target in other_team:
                            touch_list.append(Service(pmap(focus),
                                                      target=pmap(target),
                                                      is_ace=True))
                        else:
                            raise Exception("FIX THIS")
                        verify_action_deque_empty(error_on=False)
                    elif modifier in other_team:
                        touch_list.append(Service(pmap(focus),
                                                  target=pmap(modifier)))
                        set_focus(modifier)
                        touch = Defense
                    else:
                        raise Exception("FIX THIS")

                else:
                    modifier = next_touch()

                    if modifier == "n":
                        clz = Defense if touch is Defense else Spike
                        touch_list.append(clz(pmap(focus), success=False))
                        verify_action_deque_empty(error_on=False)
                    elif modifier == "p":
                        touch_list.append(Spike(pmap(focus)))
                        verify_action_deque_empty(error_on=False)

                    if touch is Defense or touch is Set:
                        if modifier in ("s", "w"):
                            target = next_touch()
                            if target in same_team or target in other_team:
                                if target in other_team:
                                    touch = Spike
                                touch_list.append(touch(pmap(focus),
                                                        target=pmap(target),
                                                        strength=modifier))
                                set_focus(target)
                                touch = touch.next
                            else:
                                raise Exception("FIX THIS")

                        elif modifier in same_team or modifier in other_team:
                            if modifier in other_team:
                                touch = Spike
                            touch_list.append(touch(pmap(focus),
                                                    target=pmap(modifier)))
                            set_focus(target)
                            touch = touch.next
                        elif modifier == "e":
                            raise NotImplemented("FIX THIS")
                        else:
                            raise Exception("FIX THIS")

                    elif touch is Spike:
                        if modifier in ("s", "w"):
                            target = next_touch()
                            if target in other_team:
                                touch_list.append(touch(pmap(focus),
                                                        target=pmap(target),
                                                        strength=modifier))
                                set_focus(target)
                                touch = touch.next
                            else:
                                raise Exception("FIX THIS")

                        elif modifier in other_team:
                            touch_list.append(touch(pmap(focus),
                                                    target=pmap(modifier)))
                            set_focus(target)
                            touch = touch.next

                        elif modifier == "e":
                            raise NotImplemented("FIX THIS")
                        else:
                            raise Exception("FIX THIS")

                    else:
                        raise Exception("FIX THIS")

            output.append(touch_list)

        return output

    @property
    def actions(self):
        """Return actions as AbstractTouches."""
        return self._action_list

    @actions.setter
    def actions(self, *acts):
        """Set the actions."""
        self._action_list_strings = acts
        self._action_list = ActionList.parse(
            self._p1, self._p2, self._p3, self._p4, acts)

    @property
    def as_strings(self):
        """Return the ActionList as a list of strings."""
        return self._action_list_strings

    @property
    def meta(self):
        """Return metadata on the game."""
        return self._meta

    def compile_actions(self, player):
        """Find all actions related to the player and return."""
        output = {"actor": [], "target": []}

		for action in self._action_list:
			if action.actor == player:
				output["actor"].append(action)
			
			if action.target == player:
				output["target"].append(action)

        return output
