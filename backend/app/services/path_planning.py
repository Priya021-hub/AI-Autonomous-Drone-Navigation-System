from heapq import heappush, heappop

GRID_SIZE = 20


class PathPlanner:

    def __init__(self):

        self.grid = [
            [0 for _ in range(GRID_SIZE)]
            for _ in range(GRID_SIZE)
        ]

    # =====================================
    # MARK OBSTACLES
    # =====================================

    def mark_obstacles(
        self,
        detections,
        frame_width,
        frame_height
    ):

        for detection in detections:

            coords = detection["coordinates"]

            x1 = coords["x1"]
            y1 = coords["y1"]
            x2 = coords["x2"]
            y2 = coords["y2"]

            # =====================================
            # CONVERT BOUNDING BOX TO GRID
            # =====================================

            start_grid_x = int(
                (x1 / frame_width) * GRID_SIZE
            )

            end_grid_x = int(
                (x2 / frame_width) * GRID_SIZE
            )

            start_grid_y = int(
                (y1 / frame_height) * GRID_SIZE
            )

            end_grid_y = int(
                (y2 / frame_height) * GRID_SIZE
            )

            # =====================================
            # KEEP INSIDE GRID
            # =====================================

            start_grid_x = max(
                0,
                min(start_grid_x, GRID_SIZE - 1)
            )

            end_grid_x = max(
                0,
                min(end_grid_x, GRID_SIZE - 1)
            )

            start_grid_y = max(
                0,
                min(start_grid_y, GRID_SIZE - 1)
            )

            end_grid_y = max(
                0,
                min(end_grid_y, GRID_SIZE - 1)
            )

            # =====================================
            # MARK OBJECT AREA
            # =====================================

            for gy in range(
                start_grid_y,
                end_grid_y + 1
            ):

                for gx in range(
                    start_grid_x,
                    end_grid_x + 1
                ):

                    self.grid[gy][gx] = 1

        # =====================================
        # KEEP START AND GOAL OPEN
        # =====================================

        self.grid[0][0] = 0

        self.grid[GRID_SIZE - 1][GRID_SIZE - 1] = 0

    # =====================================
    # HEURISTIC FUNCTION
    # =====================================

    def heuristic(self, a, b):

        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # =====================================
    # GET NEIGHBORS
    # =====================================

    def get_neighbors(self, node):

        directions = [

            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),

            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1)
        ]

        neighbors = []

        for dx, dy in directions:

            nx = node[0] + dx
            ny = node[1] + dy

            if (
                0 <= nx < GRID_SIZE
                and
                0 <= ny < GRID_SIZE
                and
                self.grid[ny][nx] == 0
            ):

                neighbors.append((nx, ny))

        return neighbors

    # =====================================
    # A* ALGORITHM
    # =====================================

    def astar(self, start, goal):

        open_set = []

        heappush(open_set, (0, start))

        came_from = {}

        g_score = {
            start: 0
        }

        f_score = {
            start: self.heuristic(start, goal)
        }

        visited = set()

        while open_set:

            current = heappop(open_set)[1]

            if current in visited:
                continue

            visited.add(current)

            if current == goal:

                path = []

                while current in came_from:

                    path.append(current)

                    current = came_from[current]

                path.append(start)

                path.reverse()

                return path

            for neighbor in self.get_neighbors(current):

                tentative_g_score = g_score[current] + 1

                if (
                    neighbor not in g_score
                    or
                    tentative_g_score < g_score[neighbor]
                ):

                    came_from[neighbor] = current

                    g_score[neighbor] = tentative_g_score

                    f_score[neighbor] = (
                        tentative_g_score
                        +
                        self.heuristic(neighbor, goal)
                    )

                    heappush(
                        open_set,
                        (
                            f_score[neighbor],
                            neighbor
                        )
                    )

        return []

    # =====================================
    # GENERATE SAFE PATH
    # =====================================

    def generate_path(
        self,
        detections,
        frame_width,
        frame_height
    ):

        self.grid = [
            [0 for _ in range(GRID_SIZE)]
            for _ in range(GRID_SIZE)
        ]

        self.mark_obstacles(
            detections,
            frame_width,
            frame_height
        )

        start = (0, 0)

        goal = (
            GRID_SIZE - 1,
            GRID_SIZE - 1
        )

        if self.grid[start[1]][start[0]] == 1:

            start = (0, 1)

        if self.grid[goal[1]][goal[0]] == 1:

            goal = (
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )

        path = self.astar(start, goal)

        return {

            "grid": self.grid,

            "path": path
        }