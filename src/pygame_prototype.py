import pygame as pg
from math import floor
import constants as Constants
import calculations as Calculations
from typing import Optional

class PGProto:
    def __init__(self):
        pg.init()

        self.__renderer = pg.draw

        self.__display = pg.display
        self.__display.init()
        self.__display.set_caption("Map sim")

        self.__screen = self.__display.set_mode(Constants.WINDOW_SIZE)

        pg.font.init()
        self.__font = pg.font.SysFont("Scout", 28) # Change font

        self.__initialize_attributes()
        self.__is_window_running = True

    def __initialize_attributes(self) -> None:
        self.__text_range: pg.Surface
        self.__text_azimuth: pg.Surface

        self.__player_pos: Optional[Calculations.Point] = None
        self.__enemy_pos: Optional[Calculations.Point] = None

        self.__update()

    def __update(self) -> None:
        angle = Calculations.calculate_angle(self.__player_pos, self.__enemy_pos)
        meters = Calculations.calculate_distance(self.__player_pos, self.__enemy_pos)

        # angle = Calculations.angle_to_cardinal(angle)

        self.__text_range = self.__font.render(Constants.TEXT_RANGE.format(meters=meters), 1, (255, 255, 255))
        self.__text_azimuth = self.__font.render(Constants.TEXT_AZIMUTH.format(angle=angle), 1, (255, 255, 255))
        
    def __handle_events(self) -> None:
        event = pg.event.poll()
        
        if event.type == pg.QUIT:
            self.__is_window_running = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.__is_window_running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.__player_pos = event.pos
            elif event.button == 3:
                self.__enemy_pos = event.pos

            self.__update()

    def __draw_grid(self) -> None:
        for i in range(0, 600, floor(Constants.PIXELS_PER_SQUARE)):
            self.__renderer.line(self.__screen, (255, 255, 255), (0, i), (Constants.WINDOW_SIZE[0], i), 1)
            self.__renderer.line(self.__screen, (255, 255, 255), (i, 0), (i, Constants.WINDOW_SIZE[1]), 1)

    def __draw_positions(self) -> None:
        if self.__player_pos is not None:
            self.__renderer.circle(self.__screen, (255, 255, 255), self.__player_pos, 10)
        
        if self.__enemy_pos is not None:
            self.__renderer.circle(self.__screen, (220, 190, 0), self.__enemy_pos, 10)

    def __draw_line_direction(self) -> None:
        if self.__player_pos is not None and self.__enemy_pos is not None:
            self.__renderer.line(self.__screen, (0, 255, 0), self.__player_pos, self.__enemy_pos, 3)

    def __draw_interface(self) -> None:
        self.__screen.blit(self.__text_range, (10, 10))
        self.__screen.blit(self.__text_azimuth, (10, 42))

    def __render(self) -> None:
        self.__screen.fill((0, 0, 0))

        self.__draw_grid()
        self.__draw_positions()
        self.__draw_line_direction()
        self.__draw_interface()

        self.__display.flip()

    def run(self) -> None:
        while self.__is_window_running:
            self.__handle_events()
            self.__render()

    def quit(self) -> None:
        pg.font.quit()
        self.__display.quit()
        pg.quit()