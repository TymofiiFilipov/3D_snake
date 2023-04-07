import pygame
import numpy
import math
import random

#matrixes
def matrix_move(pos):
    x, y, z=pos
    return numpy.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [x, y, z, 1]])

def matrix_scale(x):
    return numpy.array([
        [x, 0, 0, 0],
        [0, x, 0, 0],
        [0, 0, x, 0],
        [0, 0, 0, 1]])

def matrix_rotate_x(x):
    return numpy.array([
        [1,           0,              0, 0],
        [0, math.cos(x),    math.sin(x), 0],
        [0, -(math.sin(x)), math.cos(x), 0],
        [0,           0,           0, 1]])

def matrix_rotate_y(x):
    return numpy.array([
        [math.cos(x), 0, -(math.sin(x)), 0],
        [          0, 1,              0, 0],
        [math.sin(x), 0,    math.cos(x), 0],
        [          0, 0,              0, 1]])

def matrix_rotate_z(x):
    return numpy.array([
        [   math.cos(x), math.sin(x), 0, 0],
        [-(math.sin(x)), math.cos(x), 0, 0],
        [              0,          0, 1, 0],
        [              0,          0, 0, 1]])

class Projection():
    def __init__(self, render):
        near=render.camera.near_plane
        far=render.camera.far_plane
        
        right=math.tan(render.camera.h_fov/2)
        left=-right

        top=math.tan(render.camera.v_fov/2)
        bottom=-top

        m00=2/(right-left)
        m11=2/(top-bottom)
        m22=(far+near)/(far-near)
        m32=-2*near*far/(far-near)

        self.projection_matrix=numpy.array([
            [m00, 0, 0, 0],
            [0, m11, 0, 0],
            [0, 0, m22, 1],
            [0, 0, m32, 0],
        ])

        w, h=render.width//2, render.height//2
        self.to_screen_matrix=numpy.array([
            [w, 0, 0, 0],
            [0, -h, 0, 0],
            [0, 0, 1, 0],
            [w, h, 0, 1],
        ])

class Object_3D():
    def __init__(self, render, color):

        self.render=render
    
        self.color=color

        self.vertexes=numpy.array([(0, 0, 0, 1), (0, 1, 0, 1), (1, 1, 0, 1), (1, 0, 0, 1),
                                   (0, 0, 1, 1), (0, 1, 1, 1), (1, 1, 1, 1), (1, 0, 1, 1)])
        
        self.faces=numpy.array([(0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 5, 1), (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4)])
    
    def screen_projection(self):

        vertexes=self.vertexes@self.render.camera.camera_matrix()
        vertexes=vertexes@self.render.projection.projection_matrix
        vertexes/=vertexes[:, -1].reshape(-1, 1)
        vertexes[(vertexes>4)|(vertexes<-4)]=0
        vertexes=vertexes@self.render.projection.to_screen_matrix
        vertexes=vertexes[:, :2]

        for i in self.faces:
            polygon=vertexes[i]
            if not numpy.any((vertexes==self.render.width//2)|(vertexes==self.render.height//2)):
                pygame.draw.polygon(self.render.sc, self.color, polygon, 3)
    
    def move(self, pos):
        self.vertexes=self.vertexes@matrix_move(pos)
    
    def scale(self, scale_to):
        self.vertexes=self.vertexes@matrix_scale(scale_to)
    
    def rotate_x(self, angle):
        self.vertexes=self.vertexes@matrix_rotate_x(angle)
    
    def rotate_y(self, angle):
        self.vertexes=self.vertexes@matrix_rotate_y(angle)
    
    def rotate_z(self, angle):
        self.vertexes=self.vertexes@matrix_rotate_z(angle)

class Camera():
    def __init__(self, render, pos):
        self.render=render

        self.pos=numpy.array([*pos, 7.49])
        self.forward=numpy.array([-0.59492522, -0.53857209, 0.59666078, 1])
        self.up=numpy.array([-0.36041508, 0.84225298, 0.40088763, 1])
        self.right=numpy.array([0.71844621, -0.02345262, 0.69518704, 1])

        self.h_fov=math.pi/3
        self.v_fov=self.h_fov*(render.height/render.width)

        self.near_plane=0.1
        self.far_plane=100

        self.speed=0.01
    
    def move(self, key):
        if key=='a':
            self.pos-=self.right*self.speed
        elif key=='d':
            self.pos+=self.right*self.speed
        elif key=='w':
            self.pos+=self.forward*self.speed
        elif key=='s':
            self.pos-=self.forward*self.speed
        elif key=='q':
            self.pos-=self.up*self.speed
        elif key=='e':
            self.pos+=self.up*self.speed
    
    def camera_rotate_y(self, angle):
        rotate=matrix_rotate_y(angle)
        self.forward=self.forward@rotate
        self.up=self.up@rotate
        self.right=self.right@rotate

    def camera_rotate_x(self, angle):
        rotate=matrix_rotate_x(angle)
        self.forward=self.forward@rotate
        self.up=self.up@rotate
        self.right=self.right@rotate
    
    def camera_rotate_z(self, angle):
        rotate=matrix_rotate_z(angle)
        self.forward=self.forward@rotate
        self.up=self.up@rotate
        self.right=self.right@rotate
    
    def matrix_move_c(self):
        x, y, z, w=self.pos
        return numpy.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])
    
    def matrix_rotate_c(self):
        rx, ry, rz, rw=self.right
        fx, fy, fz, fw=self.forward
        ux, uy, uz, uw=self.up
        return numpy.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [ 0,  0,  0, 1],
        ])
    
    def camera_matrix(self):
        return self.matrix_move_c()@self.matrix_rotate_c()

class Screen():

    def __init__(self):

        pygame.init()

        self.width=1920
        self.height=1080
        self.fps=60

        self.sc=pygame.display.set_mode((self.width, self.height))
        self.clock=pygame.time.Clock()

        self.objects=[]
    
    def cr_ob(self, x, y, color):
        n=Object_3D(self, color)
        n.move([x, 0, y])
        self.objects.append(n)
    
    def del_ob(self):
        self.objects=[]

    def create_object(self):
        self.camera=Camera(self, [18.76639991, 11.62818738, -8.3353005])
        self.projection=Projection(self)

        for i in range(12):
            self.cr_ob(-1, i-1, (255, 255, 255))
        for i in range(12):
            self.cr_ob(10, i-1, (255, 255, 255))
        for i in range(10):
            self.cr_ob(i, -1, (255, 255, 255))
        for i in range(10):
            self.cr_ob(i, 10, (255, 255, 255))
        
        if self.apple==None:
            self.apple=[random.randint(0, 9), random.randint(0, 9)]
        
        self.cr_ob(self.apple[0], self.apple[1], (255, 0, 0))

        for i in self.snake:
            self.cr_ob(i[0], i[1], (0, 255, 0))

    def draw(self):
        self.sc.fill((0, 0, 0))
        for i in self.objects:
            i.screen_projection()

    def run(self):

        r=True

        self.apple=None
        self.snake=[[5, 5], [6, 5], [7, 5]]
        self.kursor=[-1, 0]
        l=0

        while r:

            self.del_ob()

            for i in pygame.event.get():
                if i.type==pygame.QUIT:
                    r=False
                    break
            
            k=pygame.key.get_pressed()
            if k[pygame.K_a]:
                if self.snake[1]!=[self.snake[0][0], self.snake[0][1]-1]:
                    self.kursor=[0, -1]
            elif k[pygame.K_d]:
                if self.snake[1]!=[self.snake[0][0], self.snake[0][1]+1]:
                    self.kursor=[0, 1]
            if k[pygame.K_w]:
                if self.snake[1]!=[self.snake[0][0]-1, self.snake[0][1]]:
                    self.kursor=[-1, 0]
            elif k[pygame.K_s]:
                if self.snake[1]!=[self.snake[0][0]+1, self.snake[0][1]-1]:
                    self.kursor=[1, 0]
            
            if l>1:
                l=0
                self.snake.insert(0, [self.snake[0][0]+self.kursor[0], self.snake[0][1]+self.kursor[1]])
                self.snake.pop(len(self.snake)-1)
            
            self.create_object()

            self.draw()

            pygame.display.set_caption(str(self.clock.get_fps()))

            pygame.display.flip()
            self.clock.tick()

            l+=0.05
        
        pygame.quit()

if __name__=='__main__':
    main=Screen()
    main.run()