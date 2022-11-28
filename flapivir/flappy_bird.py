"""
Esta sería la clase vista. Contiene el ciclo de la aplicación y ensambla
las llamadas para obtener el dibujo de la escena.
"""
import sys
import glfw
from OpenGL.GL import *

from modelo import *
from controlador import Controller
import grafica.text_renderer as tx

numero_puntaje = int(sys.argv[1])

if __name__ == '__main__':

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, 'flapivir', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Assembling the shader program (pipeline) with both shaders
    pipeline1 = tx.TextureTextRendererShaderProgram()
    pipeline2 = es.SimpleTextureTransformShaderProgram()

    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline2.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0, 1, 0.9, 1.0)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # HACEMOS LOS OBJETOS
    pajarito = Pajarito(pipeline2,numero_puntaje)
    pipes = PipeCreator()
    fondos = FondoCreator()
    suelos = SueloCreator()
    perder = Youdied(pipeline2)
    ganar = Youwin(pipeline2)

    controlador.set_model(pajarito)

    t0 = 0
    t1=0
    contadorfondos=0
    contadorsuelos=0
    puntaje=0


    while not glfw.window_should_close(window):
        headerText = str(puntaje)
        headerCharSize = 0.1
        headerCenterX = 0
        headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
        gpuHeader = es.GPUShape().initBuffers()
        pipeline1.setupVAO(gpuHeader)
        gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
        gpuHeader.texture = gpuText3DTexture
        headerTransform = tr.matmul([tr.translate(0,0.5,0)])

        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        if pajarito.score!=puntaje:
            puntaje=pajarito.score

        fondos.create_fondo(pipeline2,contadorfondos+1)
        fondos.create_fondo(pipeline2,contadorfondos)
        suelos.create_suelo(pipeline2,contadorsuelos+1)
        suelos.create_suelo(pipeline2,contadorsuelos)

        if controlador.pause:
            dt = 0.0
        elif ti >= t1+2.5:
            pipes.create_pipe(pipeline2)
            t1=ti


        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        
        pipes.update(0.5*dt)
        pajarito.update(1.5*dt)
        fondos.update(0.2*dt)
        suelos.update(0.5*dt)

        #Reconocer la logica
        pajarito.collide(pipes,fondos,suelos)  # ---> RECORRER TODOS LOS TUBOS

        # DIBUJAR LOS MODELOS
        glUseProgram(pipeline2.shaderProgram)
        fondos.draw(pipeline2)
        pajarito.draw(pipeline2)
        pipes.draw(pipeline2)
        suelos.draw(pipeline2)

        glUseProgram(pipeline1.shaderProgram)

        glUseProgram(pipeline1.shaderProgram)
        glUniform4f(glGetUniformLocation(pipeline1.shaderProgram, "fontColor"), 1,1,1,0)
        glUniform4f(glGetUniformLocation(pipeline1.shaderProgram, "backColor"), 0,0,0,1)        
        glUniformMatrix4fv(glGetUniformLocation(pipeline1.shaderProgram, "transform"), 1, GL_TRUE, headerTransform)
        pipeline1.drawCall(gpuHeader)

        if not pajarito.alive and not pipes.on:
            glUseProgram(pipeline2.shaderProgram)
            perder.draw(pipeline2)

        if pajarito.alive and not pipes.on:
            glUseProgram(pipeline2.shaderProgram)
            ganar.draw(pipeline2)
        


        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()