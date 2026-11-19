import numpy
import moderngl
import pygame
import math
from pyglm import glm
import struct


class State:

    mainCamera = None
    mainApp = -1
# another reason to do this is because the scene can't pickle a surface, so we shouldn't reference an app
# change -1 instances to None


class App():

    def __init__(self, w, h, ctx = -1):

        pygame.init()
        self.display = pygame.display.set_mode((w, h), pygame.OPENGL | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        # context stuff
        self.ctx = ctx
        if ctx == -1:
           self.ctx = moderngl.get_context()
        
        self.ctx.enable(moderngl.BLEND)
        
        # gui stuff
        self.gui = pygame.Surface((w, h)).convert_alpha()
        self._guiSampler = self.ctx.sampler(False, False, texture=self.ctx.texture((w, h), 4))
        self._guiProgram = self.ctx.program(vertex_shader=open("shaders/defaults/gui.vs").read(),
                                            geometry_shader=open("shaders/defaults/gui.gs").read(),
                                            fragment_shader=open("shaders/defaults/gui.fs").read())
        self._guiProgram['gui'] = 0
        self._guiVAO = self.ctx.vertex_array(self._guiProgram, [])

        self.deltaTime = 1
        self._exit = False
        State.mainApp = self
    
    def Start():
        pass

    def Update():
        pass

    def Exit(self):
        self._exit = True

    def _OnRender(self):
        self.ctx.clear(0, 0, 0) # change later
        self.gui.fill((0, 0, 0, 0))

        for item in self.__dict__:
            if issubclass(type(self.__dict__[item]), RenderObject):
                self.__dict__[item].render()
        
            if issubclass(type(self.__dict__[item]), Camera):
                self.__dict__[item].updateViewMatrix()
        
        # draw gui

        self.OnGui()

        self._guiSampler.texture.write(pygame.image.tobytes(self.gui, "RGBA", True), self.display.get_size())

        self.ctx.disable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self._guiSampler.use(0)
        self._guiVAO.render(moderngl.POINTS, vertices=1)

        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        
        pygame.display.flip()
    
    def OnGui(self):
        pass
    
    def _PollEvent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.Exit()
                exit()
        

    def Run(self):
        self.Start()
        while not self._exit:
            self._PollEvent()
            self.Update(self.deltaTime)
            self._OnRender()
            self.deltaTime = 1 / (self.clock.get_fps() if (self.clock.get_fps() != 0) else 60)
            self.clock.tick()


# default implementation, its pretty hard to abstract this
class Shader():

    def __init__(self, diffuseTexture = "", path = "shaders/defaults/default.fs"):

        self.program = State.mainApp.ctx.program(vertex_shader=open("shaders/defaults/default.vs").read(),
                                                 fragment_shader=open(path).read())

        # shader specific
        try:
            _texture = pygame.image.load(diffuseTexture).convert_alpha()
        except:
            _texture = pygame.image.load("textures/default.png")

        self.sampler = State.mainApp.ctx.sampler(False, False, texture=State.mainApp.ctx.texture(_texture.get_size(), 4, pygame.image.tobytes(_texture, 'RGBA', True)))

    def Use(self):

        self.program['texture1'] = 0
        self.sampler.use(0)


    def updateLight(self, light, i):

        self.program[f'lights[{i}].position'] = light.position
        self.program[f'lights[{i}].color'] = light.color
        self.program[f'lights[{i}].intensity'] = light.intensity
        self.program[f'lights[{i}].enabled'] = light.enabled

    def updateLights(self, lights):

        for i in range(len(lights)):
            self.updateLight(lights[i], i)


class RenderObject():

    # should probably put more here for the opengl side of things

    def render(self):
        pass


class Camera():

    def __init__(self, aspect_ratio, fov, near, far):
        
        # parameters
        fov = math.radians(fov)

        self.aspect_ratio = aspect_ratio
        self.fov = fov
        self.near = near
        self.far = far

        # position and "rotation"
        self.right = glm.vec3(1, 0, 0)
        self.up = glm.vec3(0, 1, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.position = glm.vec3(0, 0, 0)

        # calculate the matrices
        self.updateProjMatrix()
        self.updateViewMatrix()

        if (State.mainCamera == None):
            State.mainCamera = self

    def updateProjMatrix(self):

        self.projMatrix = glm.mat4x4(
            1 / (self.aspect_ratio * math.tan(self.fov/2)), 0, 0, 0,
            0, 1 / math.tan(self.fov/2),   0, 0,
            0, 0, -1 * (self.far+self.near) / (self.far-self.near), -1,
            0, 0, -2 * self.far * self.near / (self.far-self.near), 0
        )
    
    def updateViewMatrix(self):

        self.viewMatrix = glm.lookAt( self.position, self.position + self.forward, self.up )
    
    def updateProgramMatrix(self, shader):

        shader.program['projectionM'] = struct.unpack('16f', self.projMatrix.to_bytes())
        shader.program['viewM'] = struct.unpack('16f', self.viewMatrix.to_bytes())


class Billboard(RenderObject):

    def __init__(self, position, size, texturePath): # a fix is to add App to the 

        super().__init__()

        ctx = moderngl.get_context()

        self.size = size
        self.position = position

        self.program = ctx.program(vertex_shader=open("shaders/defaults/billboard.vs").read(),
                                   geometry_shader=open("shaders/defaults/billboard.gs").read(),
                                   fragment_shader=open("shaders/defaults/billboard.fs").read())

        self.vao = ctx.vertex_array(self.program, [])

        try:
            _texture = pygame.image.load(texturePath).convert_alpha()
        except:
            _texture = pygame.image.load(Shader.defaultTexturePath+"/default.png").convert_alpha()
        _texture = ctx.texture(_texture.get_size(), 4, pygame.image.tobytes(_texture, 'RGBA', True))

        self.sampler = ctx.sampler(repeat_x=False, repeat_y=False, texture=_texture)

        self.program['billTex'] = 0
        self.program['size'] = size

        self.program['projectionM'] = struct.unpack('16f', State.mainCamera.projMatrix.to_bytes()) # consider self.scene --> activeScene?
    
    def render(self):
        self.sampler.use(0)

        self.program['viewM'] = struct.unpack('16f', State.mainCamera.viewMatrix.to_bytes())
        self.program['position'] = self.position

        State.mainApp.ctx.disable(moderngl.CULL_FACE)
        self.vao.render(mode=moderngl.POINTS, vertices=1)
        State.mainApp.ctx.enable(moderngl.CULL_FACE)


SUNLIGHT, POINT = 0, 1

class Light(RenderObject):

    def __init__(self, position, color, intensity):
        self.position = glm.vec3(position)
        self.color = color
        self.intensity = intensity
        self.enabled = True

        self.lightBB = Billboard(self.position, (.3, .3), "textures/light.png")
    
    def render(self):
        self.lightBB.render()


class Mesh(RenderObject):

    def __init__(self, position = glm.vec3(0, 0, 0), rotation = glm.vec3(0, 0, 0), scale = 1):
        self.vertices = []
        self.position = position
        self.rotation = rotation
        self.scale = scale

    # i dont like this, do something else
    def createVAO(self, shader):
        self.shader = shader

        self.vbo = State.mainApp.ctx.buffer(numpy.asarray(self.vertices, dtype='f4'))

        self.vao = State.mainApp.ctx.vertex_array(self.shader.program, [(self.vbo , '3f 2f 3f', 'positions', 'uvcoords', 'normals')])
    
    def render(self):

        self.shader.program['projectionM'] = struct.unpack('16f', State.mainCamera.projMatrix.to_bytes()) # might move into render if needed

        self.shader.program['modelM'] = struct.unpack('16f', glm.scale(glm.translate(glm.mat4x4(), self.position), glm.vec3(self.scale)))
        self.shader.program['viewM'] = struct.unpack('16f', State.mainCamera.viewMatrix.to_bytes())

        self.shader.Use()
        self.vao.render()


#to do
def importObj(path, position = glm.vec3(0, 0, 0), rotation = glm.vec3(0, 0, 0), scale = 1):
    
    positions = []
    uvcoords = []
    normals = []

    mesh = Mesh(position, rotation, scale)

    with open(path) as objFile:

        for line in objFile:
            if line[0:2] == "v ":
                vertex = line[2:len(line)].strip().split(" ", 3)

                for i in range(3):
                    vertex[i] = float(vertex[i])
                
                positions.append(vertex)
            
            if line[0:2] == "vn":
                vertex = line[3:len(line)].strip().split(" ", 3)

                for i in range(3):
                    vertex[i] = float(vertex[i])
                
                normals.append(vertex)
            
            if line[0:2] == "vt":
                vertex = line[3:len(line)].strip().split(" ", 2)

                for i in range(2):
                    vertex[i] = float(vertex[i])
                
                uvcoords.append(vertex)
            
            if line[0:2] == "f ":
                vertex = line[2:len(line)].strip().split(" ", 2)

                for f in range(3):
                    indices = tuple(int(i) for i in vertex[f].split("/", 2)) 

                    mesh.vertices.extend(positions[indices[0]-1])
                    mesh.vertices.extend(uvcoords[indices[1]-1])
                    mesh.vertices.extend(normals[indices[2]-1])

    return mesh
