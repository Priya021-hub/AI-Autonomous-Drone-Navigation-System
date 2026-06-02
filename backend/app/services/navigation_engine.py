class NavigationEngine:

    def decide(
        self,
        object_name,
        danger,
        direction,
        path
    ):

        # No valid path
        if len(path) == 0:
            return "SEARCH NEW ROUTE"

        # Dangerous obstacle ahead
        if danger == "HIGH":
            return "STOP"

        # Obstacle on left
        if direction == "LEFT":
            return "MOVE RIGHT"

        # Obstacle on right
        if direction == "RIGHT":
            return "MOVE LEFT"

        # Obstacle in center but path exists
        if direction == "CENTER":
            return "FOLLOW PATH"

        return "FOLLOW PATH"