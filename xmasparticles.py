import pygame
from pygame.locals import *
from OpenGL.GLU import *
from OpenGL.GL import *
import random
import math

pygame.mixer.init()
xmas = pygame.mixer.Sound('Assets/christmas_music.mp3')
xmas.play(-1)
xmas.set_volume(0.1)



# Klasa cząsteczki
class Particle:
    def __init__(self, position, velocity, color, lifespan):
        self.position = position
        self.velocity = velocity
        self.color = color
        self.lifespan = lifespan

    def apply_force(self, force):
        self.velocity = [v + f for v, f in zip(self.velocity, force)]

    def update(self):
        self.position = [p + v for p, v in zip(self.position, self.velocity)]
        self.lifespan -= 1

    def is_dead(self):
        return self.lifespan <= 0


class Emitter:
    def __init__(self, position, rate, lifespan, speed_range, emitter_lifespan):
        self.position = position
        self.rate = rate
        self.lifespan = lifespan
        self.speed_range = speed_range
        self.particles = []
        self.emitter_lifespan = emitter_lifespan  

    def emit(self):
        for _ in range(self.rate):
            velocity = [
                random.uniform(-self.speed_range, self.speed_range),
                random.uniform(-self.speed_range, self.speed_range),
                random.uniform(-self.speed_range, self.speed_range),
            ]
            color = [random.random(), random.random(), random.random()]
            particle = Particle(self.position[:], velocity, color, self.lifespan)
            self.particles.append(particle)

    def update(self, external_force):
        self.emitter_lifespan -= 1
        if self.emitter_lifespan > 0:
            self.emit()
        for particle in self.particles:
            particle.apply_force(external_force)
            particle.update()
        self.particles = [p for p in self.particles if not p.is_dead()]

    def is_dead(self):
        return self.emitter_lifespan <= 0 and not self.particles

def handle_collisions(particles, sphere_center, sphere_radius):
    for particle in particles:
        distance = math.sqrt(sum([(p - c) ** 2 for p, c in zip(particle.position, sphere_center)]))
        if distance < sphere_radius:
            # Odbicie (proste) - zmiana kierunku prędkości
            particle.velocity = [0 for v in particle.velocity]

# Funkcja do rysowania cząsteczek
def draw_particles(particles):
    for particle in particles:
        glPushMatrix()
        glColor3f(*particle.color)
        glTranslatef(*particle.position)
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.05, 16, 16)
        glPopMatrix()



# Funkcja do rysowania choinki
def draw_tree():
    glPushMatrix()
    glColor3f(0, 0.5, 0)
    glTranslatef(0, -5, 0)

    quadric = gluNewQuadric()
    # Dolna część choinki
    glPushMatrix()
    gluCylinder(quadric, 3, 0, 5, 32, 32)
    glPopMatrix()

    # Środkowa część choinki
    glPushMatrix()
    glTranslatef(0, 2.5, 0)
    gluCylinder(quadric, 2.5, 0, 4, 32, 32)
    glPopMatrix()

    # Górna część choinki
    glPushMatrix()
    glTranslatef(0, 5, 0)
    gluCylinder(quadric, 2, 0, 3, 32, 32)
    glPopMatrix()

    # Pień
    glPushMatrix()
    glColor3f(0.4, 0.2, 0)
    glTranslatef(0, -3, 0)
    gluCylinder(quadric, 0.5, 0.5, 5, 32, 32)
    glPopMatrix()

    glPopMatrix()



def draw_ground():
    glPushMatrix()
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(-200, -8, -200)
    glVertex3f(-200, -8, 200)
    glVertex3f(200, -8, 200)
    glVertex3f(200, -8, -200)
    glEnd()
    glPopMatrix()


def create_firework():
    return Emitter([random.uniform(-15.0, 15.0), random.uniform(7.0, 12.0), random.uniform(-20.0, 10.0)],
                    int(random.uniform(45.0, 50.0)), random.uniform(20.0, 25.0), random.uniform(0.4, 0.5), 15)


def create_snow_emitter():
    return Emitter(
        position=[0, 20, 0],  # Wysoko nad ziemią
        rate=7,  # Liczba cząsteczek emitowanych na klatkę
        lifespan=200,  # Czas życia pojedynczej cząsteczki
        speed_range=0.1,  # Zakres prędkości (wolne opadanie)
        emitter_lifespan=float('inf')  # Emiter działa w nieskończoność
    )



def load_texture(file_name):
    texture_surface = pygame.image.load(file_name)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width, height = texture_surface.get_rect().size
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture_id




def draw_background(texture_id):
    glPushMatrix()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-70, -10, -50)
    glTexCoord2f(1, 0)
    glVertex3f(70, -10, -50)
    glTexCoord2f(1, 1)
    glVertex3f(70, 38, -50)
    glTexCoord2f(0, 1)
    glVertex3f(-70, 38, -50)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()






def main():
    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glClearColor(0, 0, 0.2, 1)  # Niebieskawe tło
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0, 0, -40)


    background_texture = load_texture("Assets/sky.jpg")  # Ładowanie tła

    
    clock = pygame.time.Clock()
    firework_timer = 0
    emitters = []
    snow_emitter = create_snow_emitter()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
       
        draw_background(background_texture)
        # Rysowanie choinki i ziemi
        draw_ground()
        draw_tree()
        
        #Śnieg
        snow_emitter.update([0, -0.001, 0])  # Siła grawitacji na cząsteczki
        handle_collisions(snow_emitter.particles, [0, 0, 0], 1)  # Kolizje z gora choinki
        handle_collisions(snow_emitter.particles, [0, -2.5, 0], 2)  # Kolizje z srodkiem choinki
        handle_collisions(snow_emitter.particles, [0, -5, 0], 3)  # Kolizje z dolem choinki
        for particle in snow_emitter.particles:
            particle.color = [1, 1, 1]  # Ustaw kolor śniegu na biały
        draw_particles(snow_emitter.particles)

        # Aktualizacja cząsteczek z emiterów
        for emitter in emitters:
            emitter.update([0, -0.01, 0])
            handle_collisions(emitter.particles, [0, 2.5 ,0], 2)
            draw_particles(emitter.particles)

        emitters = [e for e in emitters if not e.is_dead()]

        # Dodanie fajerwerków co pewien czas
        firework_timer += 1
        if firework_timer > 120:
            emitters.append(create_firework())
            pygame.mixer.music.load('Assets/fireworks.mp3')
            pygame.mixer.music.set_volume(0.2)  
            pygame.mixer.music.play()
            firework_timer = 0

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
