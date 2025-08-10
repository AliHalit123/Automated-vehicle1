

class GameState:
    """
    A class that consolidates all variables used during the game in one place.
    Eliminates the need for global variables.
    """
    def __init__(self, grid, building_positions, pedestrians, garbage):
        # Map and position data
        self.grid = grid
        self.building_positions = building_positions

        # Vehicle and target information
        self.start = None
        self.end_list = []         # There can be multiple targets
        self.vehicle = None
        self.vehicle1 = None
        self.path = []

        # Object managers
        self.pedestrians = pedestrians
        self.garbage = garbage

        # Game control variables
        self.mode = None           # "start", "end", "pedestrian", etc.
        self.start_simulation = False

        # Timing information
        self.start_time = None
        self.end_time_v1 = None
        self.end_time_v2 = None

        # Information about whether vehicles have reached the target
        self.v_reached = [False, False]

        # Counters (map/run/version)
        self.i = 0  # Map counter
        self.j = 0  # Run counter
        self.k = 0  # Version counter
