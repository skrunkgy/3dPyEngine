import pygame
import engine
from pyglm import glm

class Camera(engine.Camera):

    speed = 3
    sensitivity = .1

    rotation = glm.vec3()

    def __init__(self):
        super().__init__(800/600, 90, .1, 10000)

    def updateCam(self, deltaTime):

        direction = glm.vec3()

        # it does seem that the direction.z should be -1 when pressing w, but this will negate the cameras self.forward z component
        # which we don't want
        direction.x = 1 if pygame.key.get_pressed()[pygame.K_d] else -1 if pygame.key.get_pressed()[pygame.K_a] else 0
        direction.z = 1 if pygame.key.get_pressed()[pygame.K_w] else -1 if pygame.key.get_pressed()[pygame.K_s] else 0

        direction *= deltaTime * Camera.speed

        self.position += self.right * direction.x + self.forward * direction.z

        rel = pygame.mouse.get_rel()

        Camera.rotation.x += rel[1] * Camera.sensitivity
        Camera.rotation.y -= rel[0] * Camera.sensitivity

        if Camera.rotation.x > 89.9:
            Camera.rotation.x = 89.9
        elif Camera.rotation.x < -89.9:
            Camera.rotation.x = -89.9

        self.forward = glm.rotateY(glm.vec3(0, 0, -1), glm.radians(Camera.rotation.y))
        self.forward = glm.rotate(self.forward, glm.radians(Camera.rotation.x), glm.cross(self.up, self.forward))

        self.right = glm.normalize(glm.cross(self.forward, self.up))


class Program(engine.App):

    # or just define defaults here

    def Start(self):

        self.camera = Camera() # own implementation
        self.joe = engine.Billboard((0, 0, -10), (1, 1,), "textures/huehsleep.png")
        self.objectOne = engine.importObj("models/Mort.obj", position = (-2, 0, -3), scale = .3)
        self.objectOne.createVAO(engine.Shader("textures/texture_001.png"))

        self.objectTwo = engine.importObj("models/cube.obj", position = (2, 0, -3), scale = .3)
        self.objectTwo.createVAO(engine.Shader(""))

        self.lights = [engine.Light((-2, 3, -1), (0, 0, 1), 3),
                       engine.Light((-1, 2, -2), (0, 1, 0), 1),
                       engine.Light((-3, 2, -2), (1, 0, 0), 1)]
        
         
        self.objectOne.shader.updateLights(self.lights)
        self.objectTwo.shader.updateLights(self.lights)

        pygame.mouse.set_visible(0)
        pygame.event.set_grab(1)
    
    def Update(self, deltaTime):
        self.camera.updateCam(deltaTime)

        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            Program.Exit(self)
        
        pygame.display.set_caption(f'{1/deltaTime} fps')
    
    def OnGui(self):
        self.gui.blit(pygame.image.load("textures/huehsleep.png"), (0, 0))
        pygame.draw.rect(self.gui, (255,255,255), (399, 299, 2, 2))


app = Program(800, 600)

app.Run()
