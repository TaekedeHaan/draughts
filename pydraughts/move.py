class Move(object):
    def __init__(self, locations=None, directions=None, captures=None):
        if locations is None:
            locations = []

        if captures is None:
            captures = []

        if directions is None:
            directions = []

        if isinstance(directions, str):
            directions = [directions]

        if isinstance(captures, int):
            captures = [captures]

        self.locations = locations
        self.directions = directions
        self.captures = captures

    def is_capture_move(self):
        return len(self.captures) > 0

    def append(self, other_move):
        if len(self.locations) == 0:
            self.locations.extend(other_move.locations)
            self.directions.extend(other_move.directions)
            self.captures.extend(other_move.captures)
            return

        if self.locations[-1] != other_move.locations[0]:
            raise Exception(
                "Cannot append move: this move ends at %s, while the other starts at %s"
                % (self.locations[-1], other_move.locations[0])
            )

        self.locations.extend(other_move.locations[1:])
        self.directions.extend(other_move.directions)
        self.captures.extend(other_move.captures)

    def split(self):
        """split a move into a list of sub moves"""
        moves = []
        for i, (loc_start, loc_end) in enumerate(
            zip(self.locations, self.locations[1:])
        ):
            captures = [self.captures[i]] if self.captures else None
            directions = [self.directions[i]] if self.directions else None

            move = Move([loc_start, loc_end], directions, captures)
            moves.append(move)
        return moves

    def is_empty(self):
        return len(self.locations) == 0

    def copy(self):
        return Move(self.locations.copy(), self.directions.copy(), self.captures.copy())

    def get_notation(self):
        my_string = ""
        sep = "-" if (not self.is_capture_move()) else "x"
        for i, location in enumerate(self.locations):
            if i < (len(self.locations) - 1):
                my_string += "%d%s" % (location, sep)
            else:
                my_string += "%d" % (location)
        return my_string

    def __str__(self):
        # for debugging:
        return "move: locations %s, directions: %s, captures: %s" % (
            self.locations,
            self.directions,
            self.captures,
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
