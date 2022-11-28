from OpenGL.GL import *
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath
import grafica.scene_graph as sg

import random
from typing import List

class Pajarito(object):
    def __init__(self, pipeline,numero_puntaje):
        # Figuras básicas
        shape_bird=bs.createTextureQuad(1,1)
        gpu_bird = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_bird)
        gpu_bird.fillBuffers(shape_bird.vertices, shape_bird.indices, GL_STATIC_DRAW)
        gpu_bird.texture=es.textureSimpleSetup(
            getAssetPath("rene.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        
        bird = sg.SceneGraphNode('pajarito')
        bird.transform = np.matmul(tr.translate(-0.5,0,1), tr.scale(0.15,0.15,0))
        bird.childs=[gpu_bird]

        transform_bird = sg.SceneGraphNode('pajaritoTR')
        transform_bird.childs += [bird]

        self.numero_puntaje=numero_puntaje
        self.model = transform_bird
        self.x=-0.5
        self.pos = 0
        self.y = 0
        self.alive = True
        self.score = 0

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def modifymodel(self):
        # Transforma la geometria del modelo segun las variables internas
        # Podria ser una funcion hiper gigante
        self.model.transform = tr.translate(0, self.y, 0)

    def update(self, dt):
        if self.pos != self.y:
            if self.pos>self.y:
                self.y+=2*dt
            elif self.pos-self.y < 0.005:
                self.y=self.pos
        else:
            self.y-=0.5*dt
            self.pos=self.y
        
        # modificar de manera constante al modelo
        # aqui deberia llamar a tr.translate
        self.modifymodel()

    def move_up(self):
        if not self.alive:
            return
        self.pos += 0.3

    def collide(self, pipes: 'PipeCreator', fondos: 'FondoCreator', suelos: 'SueloCreator'):
        if not pipes.on:  # Si el jugador perdió, no detecta colisiones
            return
        if self.y <-0.825:
            pipes.die()
            self.alive = False
        
        deleted_pipes = []
        deleted_fondos = []
        deleted_suelos = []
        for e in pipes.pipes:
            if -0.725<e.pos_x<-0.275 and (e.pos_y+0.225<self.y or e.pos_y-0.225>self.y):
                """
                En este caso, podríamos hacer alguna pestaña de alerta al usuario,
                cambiar el fondo por alguna textura, o algo así, en este caso lo que hicimos fue
                cambiar el color del fondo de la app por uno rojo.
                """
                pipes.die()
                self.alive = False
            
            elif -0.65>e.pos_x and e.pos_y+0.225>self.y and e.pos_y-0.225<self.y and not e.punto:
                e.punto=True
                self.score+=1

            elif e.pos_x <= -1:
                deleted_pipes.append(e)

            elif self.score==self.numero_puntaje:
                pipes.win()

        pipes.delete(deleted_pipes)

        for a in fondos.fondos:
            if a.pos_x <= -2:
                deleted_fondos.append(a)
        fondos.delete(deleted_fondos)

        for b in suelos.suelos:
            if b.pos_x <= -2:
                deleted_suelos.append(b)
        suelos.delete(deleted_suelos)


class Pipe(object):

    def __init__(self, pipeline):
        shape_tubo1=bs.createTextureQuad(1,1)
        gpu_tubo1 = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_tubo1)
        gpu_tubo1.fillBuffers(shape_tubo1.vertices, shape_tubo1.indices, GL_STATIC_DRAW)
        gpu_tubo1.texture=es.textureSimpleSetup(
            getAssetPath("tuboabajo.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        
        shape_tubo2=bs.createTextureQuad(1,1)
        gpu_tubo2 = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_tubo2)
        gpu_tubo2.fillBuffers(shape_tubo2.vertices, shape_tubo2.indices, GL_STATIC_DRAW)
        gpu_tubo2.texture=es.textureSimpleSetup(
            getAssetPath("tuboarriba.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        
        espacio = random.uniform(-0.65,0.75)
        size1=1+(espacio-0.3)
        size2=1-(espacio+0.3)

        #Tubos
        tuboa=sg.SceneGraphNode('tuboa')
        tuboa.childs+=[gpu_tubo1]

        tubob=sg.SceneGraphNode('tubob')
        tubob.childs+=[gpu_tubo2]

        tubo2=sg.SceneGraphNode('tubo2')
        tubo2.transform=np.matmul(tr.translate(0,espacio+0.3+size2/2,1),tr.scale(0.3,size2,1))
        tubo2.childs+=[tubob]

        tubo1=sg.SceneGraphNode('tubo1')
        tubo1.transform=np.matmul(tr.translate(0,espacio-(0.3+size1/2),1),tr.scale(0.3,size1,1))
        tubo1.childs+=[tuboa]

        tubosjuntos=sg.SceneGraphNode('tubosjuntos')
        tubosjuntos.childs+=[tubo2,tubo1]

        transform_tubosjuntos = sg.SceneGraphNode('tubosjuntosTR')
        transform_tubosjuntos.childs += [tubosjuntos]

        self.model=transform_tubosjuntos
        self.pos_x = 1
        self.pos_y = espacio
        self.punto = False

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def update(self, dt):
        self.pos_x -= dt

class PipeCreator(object):
    pipes: List['Pipe']

    def __init__(self):
        self.pipes = []
        self.on = True

    def die(self):
        self.on = False
    
    def win(self):
        self.on = False

    def create_pipe(self, pipeline):
        if len(self.pipes) >= 3 or not self.on:
            return
        self.pipes.append(Pipe(pipeline))

    def draw(self, pipeline):
        for k in self.pipes:
            k.draw(pipeline)

    def update(self, dt):
        for k in self.pipes:
            k.update(dt)

    def delete(self, d):
        if len(d) == 0:
            return
        remain_pipes = []
        for k in self.pipes:  # Recorro todos los huevos
            if k not in d:  # Si no se elimina, lo añado a la lista de huevos que quedan
                remain_pipes.append(k)
        self.pipes = remain_pipes  # Actualizo la lista

class Fondo(object):

    def __init__(self, pipeline,contadorfondos):
        shape_fondo=bs.createTextureQuad(1,1)
        gpu_fondo = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_fondo)
        gpu_fondo.fillBuffers(shape_fondo.vertices, shape_fondo.indices, GL_STATIC_DRAW)
        gpu_fondo.texture=es.textureSimpleSetup(
            getAssetPath("fondo.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        fondo=sg.SceneGraphNode('fondo')
        fondo.transform=tr.scale(2,2,0)
        fondo.childs+=[gpu_fondo]

        transform_fondo=sg.SceneGraphNode('fondoTR')
        transform_fondo.childs += [fondo]

        self.model=transform_fondo
        
        if contadorfondos%2==0:
            self.pos_x = 0
        else:
            self.pos_x = 2

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, -1)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def update(self, dt):
        self.pos_x -= dt

class FondoCreator(object):
    fondos: List['Fondo']

    def __init__(self):
        self.fondos = []
        self.on = True

    def create_fondo(self, pipeline, contadorfondos):
        if len(self.fondos) >= 2 or not self.on:
            return
        else:
            self.fondos.append(Fondo(pipeline,contadorfondos))

    def draw(self, pipeline):
        for k in self.fondos:
            k.draw(pipeline)

    def update(self, dt):
        for k in self.fondos:
            k.update(dt)

    def delete(self, d):
        if len(d) == 0:
            return
        remain_fondos = []
        for k in self.fondos:
            if k not in d:
                remain_fondos.append(k)
        self.fondos = remain_fondos

class Suelo(object):

    def __init__(self, pipeline,contadorsuelos):
        shape_suelo=bs.createTextureQuad(1,1)
        gpu_suelo = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_suelo)
        gpu_suelo.fillBuffers(shape_suelo.vertices, shape_suelo.indices, GL_STATIC_DRAW)
        gpu_suelo.texture=es.textureSimpleSetup(
            getAssetPath("suelo.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        suelo=sg.SceneGraphNode('suelo')
        suelo.transform=np.matmul(tr.translate(0,-0.95,1),tr.scale(2,0.1,0))
        suelo.childs+=[gpu_suelo]

        transform_suelo=sg.SceneGraphNode('sueloTR')
        transform_suelo.childs += [suelo]

        self.model=transform_suelo
        
        if contadorsuelos%2==0:
            self.pos_x = 0
        else:
            self.pos_x = 2

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, -1)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def update(self, dt):
        self.pos_x -= dt

class SueloCreator(object):
    suelos: List['Suelo']

    def __init__(self):
        self.suelos = []
        self.on = True

    def create_suelo(self, pipeline, contadorsuelos):
        if len(self.suelos) >= 2 or not self.on:
            return
        else:
            self.suelos.append(Suelo(pipeline,contadorsuelos))

    def draw(self, pipeline):
        for k in self.suelos:
            k.draw(pipeline)

    def update(self, dt):
        for k in self.suelos:
            k.update(dt)

    def delete(self, d):
        if len(d) == 0:
            return
        remain_suelos = []
        for k in self.suelos:
            if k not in d:
                remain_suelos.append(k)
        self.suelos = remain_suelos

class Youdied(object):
    def __init__(self, pipeline):
        shape_lose=bs.createTextureQuad(1,1)
        gpu_lose = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_lose)
        gpu_lose.fillBuffers(shape_lose.vertices, shape_lose.indices, GL_STATIC_DRAW)
        gpu_lose.texture=es.textureSimpleSetup(
            getAssetPath("youdied.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        
        lose = sg.SceneGraphNode('perder')
        lose.transform = tr.scale(2,2,0)
        lose.childs=[gpu_lose]

        transform_lose = sg.SceneGraphNode('perderTR')
        transform_lose.childs += [lose]

        self.model = transform_lose

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

class Youwin(object):
    def __init__(self, pipeline):
        shape_win=bs.createTextureQuad(1,1)
        gpu_win = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_win)
        gpu_win.fillBuffers(shape_win.vertices, shape_win.indices, GL_STATIC_DRAW)
        gpu_win.texture=es.textureSimpleSetup(
            getAssetPath("youwin.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        
        win = sg.SceneGraphNode('ganar')
        win.transform = tr.scale(2,2,0)
        win.childs=[gpu_win]

        transform_win = sg.SceneGraphNode('ganarTR')
        transform_win.childs += [win]

        self.model = transform_win

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')