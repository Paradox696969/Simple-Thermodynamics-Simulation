import pygame
import math

class Vec2D:
    def __init__(self, x, y):
        self.vec = [x, y]
    
    def __getitem__(self, i):
        return self.vec[i]
    
    def __add__(self, vec):
        return Vec2D(self.vec[0] + vec[0], self.vec[1] + vec[1])
    
    def __mul__(self, scalar):
        if isinstance(scalar, float) or isinstance(scalar, int):
            return Vec2D(self.vec[0]*scalar, self.vec[1]*scalar)
        elif isinstance(scalar, Vec2D):
            return Vec2D(self.vec[0]*scalar[0], self.vec[1]*scalar[1])
    
    def replace(self, point, value):
        self.vec[point] = value

    
    def vecList(self):
        return self.vec

class Border:
    def __init__(self, mass, pos, size, vel):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos.vec, size.vec)
        self.vel = vel
        self.mass = mass
        self.e_k = self.vel * self.vel * self.mass
        self.e_k = self.e_k*(1/2)
    
    def accelerate(self, force, time):
        mt = time/self.mass
        self.vel = self.vel + force*mt
    
    def update(self, time):
        self.pos = self.pos + self.vel*time
        self.e_k = self.vel * self.vel * self.mass
        self.e_k = self.e_k*(1/2)
        self.rect = pygame.Rect(self.pos.vec, self.size.vec)

class Particle:
    def __init__(self, mass=1, pos=Vec2D(0, 0), vel=Vec2D(0, 0), size=Vec2D(1, 1), color=(255, 0, 0)):
        self.mass = mass
        self.pos = pos
        self.vel = vel
        self.size = size
        self.color = color
        self.angle = math.atan2(self.vel[1], self.vel[0])
        self.rect = pygame.Rect(self.pos.vec, self.size.vec)
        self.x_points = [[self.pos[0]+1, self.pos[1]+self.size[1]//2], [self.pos[0]+self.size[0]-1, self.pos[1]+self.size[1]//2]]
        self.y_points = [[self.pos[0]+self.size[0] // 2, self.pos[1]+1], [self.pos[0]+self.size[0] // 2, self.pos[1]+self.size[1]-1]]
        self.e_k = self.vel * self.vel * self.mass * (1/2)
    
    def accelerate(self, acceleration, time):
        mt = time / self.mass
        self.vel = self.vel + acceleration*mt
    
    def updatePos(self, time, blacklist, borders, particles, heat_regions, detector_regions, i, C, loss):
        self.e_k = self.vel * self.vel * self.mass
        self.e_k = self.e_k*(1/2)
        energy=0
        self.angle = math.atan2(self.vel[1], self.vel[0])

        for j in range(len(particles)):
            if j != i or j not in blacklist:
                if particles[i].rect.colliderect(particles[j].rect):
                    pa = particles[i].vel * particles[i].mass
                    pb = particles[j].vel * particles[j].mass
                    massrec = 1/(particles[i].mass + particles[j].mass)
                    va = (pa + pb + (particles[j].vel + particles[i].vel*-1) * (particles[j].mass * C))* massrec
                    vb = (pa + pb + (particles[i].vel + particles[j].vel*-1) * (particles[i].mass * C))* massrec

                    particles[i].vel = va
                    particles[j].vel = vb
                
        for border in borders:
            collidedx = Vec2D(0, 0)
            collidedy = Vec2D(0, 0)
            for point in range(2):
                if border.rect.collidepoint(particles[i].y_points[point]):
                    particles[i].vel = Vec2D(particles[i].vel[0], -particles[i].vel[1]*loss)
                    # border.accelerate(Vec2D(0,  -particles[i].vel[1]*(1-loss)*particles[i].mass), 1)
                    collidedy.replace(point, 1)
                if border.rect.collidepoint(particles[i].x_points[point]):
                    particles[i].vel = Vec2D(-particles[i].vel[0]*loss, particles[i].vel[1])
                    # border.accelerate(Vec2D(-particles[i].vel[0]*(1-loss)*particles[i].mass, 0), 1)
                
            # collision logic---------------------->
            if collidedx[0] and collidedx[1] and collidedy[0] and collidedy[1]:
                particles[i].pos = spawnpoint
        self.angle = math.atan2(self.vel[1], self.vel[0])

        
        for heat_region in heat_regions:
            en_add = heat_region.energy_add
            energy = math.sqrt(self.e_k[0]**2+self.e_k[1]**2)
            if self.rect.colliderect(heat_region.rect):
                dEnergy = (heat_region.energy_reserve - energy)*en_add*time
                heat_region.energy_reserve -= dEnergy
                dEnergy1 = math.sqrt(abs(dEnergy))
                dEnergy1 *= -1 if dEnergy < 0 else 1
                self.accelerate(Vec2D(dEnergy1*math.cos(self.angle), dEnergy1*math.sin(self.angle)), 2)
            
            
            


        self.pos = self.pos + self.vel*time
        self.rect = pygame.Rect(self.pos.vec, self.size.vec)
        self.x_points = [[self.pos[0], self.pos[1]+self.size[1]//2], [self.pos[0]+self.size[0], self.pos[1]+self.size[1]//2]]
        self.y_points = [[self.pos[0]+self.size[0] // 2, self.pos[1]], [self.pos[0]+self.size[0] // 2, self.pos[1]+self.size[1]]]
                
        for detector in detector_regions:
            if detector.rect.colliderect(self.rect):
                detector.updateFlux(1, self.e_k)
    
    def collide(self, particle):
        if self.rect.colliderect(particle.rect):
            pass
            
class HeatRegion:
    def __init__(self, energy_add, energy_reserve, pos, size, vel=Vec2D(0, 0)):
        self.energy_add = energy_add
        self.energy_reserve = energy_reserve
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos.vec, self.size.vec)
        self.vel = vel
        self.colour_const = 100/abs(self.energy_reserve)
    
    def update(self, time):
        self.pos = self.pos + self.vel * time
        self.rect = pygame.Rect(self.pos.vec, self.size.vec)

class DetectorRegion:
    def __init__(self, pos, size, id):
        self.id = id
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos.vec, self.size.vec)
        self.flux = []
        self.energy_flux = []
        self.total_energy_flux = []
        self.flux_0 = 0
        self.energy_flux_0 = Vec2D(0, 0)
        self.total_energy_flux_0 = 0
    
    def updateFlux(self, p_flux, e_flux):
        self.flux_0 += p_flux
        self.energy_flux_0 += e_flux * (1/(1_000_000*500))
        self.total_energy_flux_0 = math.sqrt(self.energy_flux_0[0]**2 + self.energy_flux_0[1]**2)
    
    def compile_results(self):
        self.flux.append(self.flux_0)
        self.energy_flux.append(self.energy_flux_0)
        self.total_energy_flux.append(self.total_energy_flux_0)
        self.flux_0 = 0
        self.energy_flux_0 = Vec2D(0, 0)
        self.total_energy_flux_0 = 0
    
    def reset(self):
        self.flux = []
        self.energy_flux = []
        self.total_energy_flux = []
