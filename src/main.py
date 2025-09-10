import pygame as pg
from math import sqrt, atan2, pi, floor

SQUARE_PIXEL = 600 / 7
RADIUS_OF_OUTER_CIRCLE = 600 * sqrt(2)
METERS_PER_SQUARE = 170

def map_angle(angle: float) -> float | str:
    # angle = ((angle + 180) % 360) - 180
    mapped = -1
    
    if angle >= -180 and angle < 0:
        mapped = -angle
    elif angle > 0 and angle <= 180:
        mapped = -angle + 360

    mapped = round(mapped, 2)

    if abs(mapped - 0) < 1.0:
        mapped = 'N'
    elif abs(mapped - 90) < 1.0:
        mapped = 'E'
    elif abs(mapped - 180) < 1.0:
        mapped = 'S'
    elif abs(mapped - 270) < 1.0:
        mapped = 'W'

    return mapped

def main() -> None:
    pg.init()

    display = pg.display
    display.init()
    display.set_caption("Map sim")

    screen = display.set_mode((600, 600))

    pg.font.init()

    font1 = pg.font.SysFont("Scout", 28)

    range_meters = "Range: {meters}"
    azimuth_text = "Azimuth: {angle}"
    meters = -1
    angle: float | str = -1

    renderer = pg.draw
    
    pos1, pos2 = (-1, -1), (-1, -1)

    while True:
        event = pg.event.poll()
        screen.fill((0, 0, 0))

        if event.type == pg.QUIT:
            break
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            break
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos1 = event.pos
            elif event.button == 3:
                pos2 = event.pos

        for i in range(0, 600, floor(SQUARE_PIXEL)):
            renderer.line(screen, (255, 255, 255), (0, i), (600, i), 1)
            renderer.line(screen, (255, 255, 255), (i, 0), (i, 600), 1)

        if pos1 != (-1, -1):
            renderer.circle(screen, (255, 255, 255), pos1, 10)
        if pos2 != (-1, -1):
            renderer.circle(screen, (220, 190, 0), pos2, 10)

        if pos1 != (-1, -1) and pos2 != (-1, -1):
            renderer.line(screen, (0, 255, 0), pos1, pos2, 3)
            meters = (sqrt(
                ( (pos1[0] - pos2[0]) / SQUARE_PIXEL )**2 + \
                ( (pos1[1] - pos2[1]) / SQUARE_PIXEL )**2
                ) * METERS_PER_SQUARE).__round__(2)
            
            angle = (180 / pi * atan2(
                (pos1[0] - pos2[0]) / SQUARE_PIXEL,
                (pos1[1] - pos2[1]) / SQUARE_PIXEL
            )).__round__(2)

        mapped_angle = map_angle(angle)

        rendered_text = font1.render(range_meters.format(meters=meters), 1, (255, 255, 255))
        screen.blit(rendered_text, (10, 10))

        rendered_text = font1.render(azimuth_text.format(angle=mapped_angle), 1, (255, 255, 255))
        screen.blit(rendered_text, (10, 42))
        
        display.flip()

    pg.font.quit()
    display.quit()
    pg.quit()

if __name__ == "__main__":
    main()