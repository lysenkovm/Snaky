# Test-Grid
class GridLine(pygame.sprite.Sprite):
    def __init__(self, group, rect, pos, coord_n):
        super().__init__(group)
        self.rect = self.gen_rect(rect, pos, coord_n)
        x = self.rect[1][0] - self.rect[0][0]
        y = self.rect[1][1] - self.rect[0][1]
        x += 1 if x == 0 else 0
        y += 1 if y == 0 else 0
        self.image = pygame.Surface((x, y))
        self.image.fill("red")

    def gen_rect(self, rect, pos, coord_n):
        line_rect = tuple(map(lambda p: move_coords(p, coord_n, 1, pos), rect))
        return line_rect


def gen_grid(screen_size, sq_size, group):
    hor_rect_factors_points = ((0, 0), (1, 0))
    hor_rect = tuple(
        [
            (p[0] * screen_size[0], p[1] * screen_size[0])
            for p in hor_rect_factors_points
        ]
    )
    for i in range(0, screen_size[1], sq_size):
        GridLine(group, hor_rect, i, 1)

    vert_rect_factors_points = ((0, 0), (0, 1))
    vert_rect = tuple(
        [
            (p[0] * screen_size[0], p[1] * screen_size[1])
            for p in vert_rect_factors_points
        ]
    )
    for j in range(0, screen_size[0], sq_size):
        GridLine(group, vert_rect, j, 0)


# Test-Grid