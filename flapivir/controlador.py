"""
Clase controlador, obtiene el input, lo procesa, y manda los mensajes
a los modelos.
"""

from modelo import Pajarito, PipeCreator, FondoCreator
import glfw
import sys
from typing import Union


class Controller(object):
    model: Union['Pajarito', None]
    pipes: Union['PipeCreator', None]
    fondos: Union['FondoCreator',None]

    def __init__(self):
        self.model = None
        self.pipes = None
        self.fondos=None
        self.pause = True

    def set_model(self, m):
        self.model = m

    def set_pipes(self, e):
        self.pipes = e

    def on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            # Controlador modifica al modelo
            elif key == glfw.KEY_UP:
                self.model.move_up()

            elif key == glfw.KEY_P:
                self.pause = not self.pause

            # Raton toca la pantalla....
            else:
                print('Unknown key')

    def cursor_pos_callback(self, window, x, y):
        self.mousePos = (x, y)