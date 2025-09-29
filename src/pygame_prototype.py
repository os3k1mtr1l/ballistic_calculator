import pygame as pg
from math import floor
import constants as Constants
import calculations as Calculations
from typing import Optional

class PGProto:
    def __init__(self):
        pg.init()

        self._renderer = pg.draw

        self._display = pg.display
        self._display.init()
        self._display.set_caption("Map sim")

        self._screen = self._display.set_mode(Constants.WINDOW_SIZE)

        pg.font.init()
        self._font = pg.font.SysFont("Scout", 28) # Change font

        self._initialize_attributes()
        self._is_window_running = True

    def _initialize_attributes(self) -> None:
        self._text_range: pg.Surface
        self._text_azimuth: pg.Surface

        self._player_pos: Optional[Calculations.Point] = None
        self._enemy_pos: Optional[Calculations.Point] = None

        self._update()

    def _update(self) -> None:
        angle = Calculations.calculate_angle(self._player_pos, self._enemy_pos)
        meters = Calculations.calculate_distance(self._player_pos, self._enemy_pos)

        # angle = Calculations.angle_to_cardinal(angle)

        self._text_range = self._font.render(Constants.TEXT_RANGE.format(meters=meters), 1, (255, 255, 255))
        self._text_azimuth = self._font.render(Constants.TEXT_AZIMUTH.format(angle=angle), 1, (255, 255, 255))
        
    def _handle_events(self) -> None:
        event = pg.event.poll()
        
        if event.type == pg.QUIT:
            self._is_window_running = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self._is_window_running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._player_pos = event.pos
            elif event.button == 3:
                self._enemy_pos = event.pos

            self._update()

    def _draw_grid(self) -> None:
        for i in range(0, 600, floor(Constants.PIXELS_PER_SQUARE)):
            self._renderer.line(self._screen, (255, 255, 255), (0, i), (Constants.WINDOW_SIZE.x, i), 1)
            self._renderer.line(self._screen, (255, 255, 255), (i, 0), (i, Constants.WINDOW_SIZE.y), 1)

    def _draw_positions(self) -> None:
        if self._player_pos is not None:
            self._renderer.circle(self._screen, (255, 255, 255), self._player_pos, 10)
        
        if self._enemy_pos is not None:
            self._renderer.circle(self._screen, (220, 190, 0), self._enemy_pos, 10)

    def _draw_line_direction(self) -> None:
        if self._player_pos is not None and self._enemy_pos is not None:
            self._renderer.line(self._screen, (0, 255, 0), self._player_pos, self._enemy_pos, 3)

    def _draw_interface(self) -> None:
        self._screen.blit(self._text_range, (10, 10))
        self._screen.blit(self._text_azimuth, (10, 42))

    def _render(self) -> None:
        self._screen.fill((0, 0, 0))

        self._draw_grid()
        self._draw_positions()
        self._draw_line_direction()
        self._draw_interface()

        self._display.flip()

    def run(self) -> None:
        while self._is_window_running:
            self._handle_events()
            self._render()

    def quit(self) -> None:
        pg.font.quit()
        self._display.quit()
        pg.quit()