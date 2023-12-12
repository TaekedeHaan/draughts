import pygame


class Controller(object):
    def __init__(self):
        pass

    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Human player received quit event")
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                # click outside of the squares
                if mouse_pos is None:
                    continue
