import pygame
import math
import pandas
import random
import sys
from Engine import *
pygame.init()

# define pygame screen and clock
screen = pygame.display.set_mode((420, 440))
pygame.display.set_caption("A Simple Thermodynamics Simulation")
clock = pygame.time.Clock()

# set frame-rate to determine speed
fps = 10000

# define lists of objects and regions
particles = []
borders = []
heat_regions = []
detector_regions = []


# Detector Regions -------------------------------------------------------------------->

# Dual Container Detectors
detector_regions.append(DetectorRegion(Vec2D(0, 0), Vec2D(420, 220), 1))
detector_regions.append(DetectorRegion(Vec2D(0, 220), Vec2D(420, 220), 2))
detector_regions.append(DetectorRegion(Vec2D(0, 0), Vec2D(420, 440), 3))

# Single Container Detectors
# detector_regions.append(DetectorRegion(Vec2D(0, 0), Vec2D(420, 200), 1))


# Heat Regions ------------------------------------------------------------------------>

# Dual Container Heat Region
heat_regions.append(HeatRegion(0.5, 9e+6, Vec2D(170, 180), Vec2D(80, 80), Vec2D(0, 0)))

# Single Container Heat Region
# heat_regions.append(HeatRegion(0.5, 9e+7, Vec2D(170, 65), Vec2D(80, 80), Vec2D(0, 0)))


# Border Regions ---------------------------------------------------------------------->

# Dual container borders
borders.append(Border(3000, Vec2D(0, 0), Vec2D(400, 20), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(0, 0), Vec2D(20, 200), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(400, 0), Vec2D(20, 200), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(20, 180), Vec2D(150, 20), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(250, 180), Vec2D(150, 20), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(150, 200), Vec2D(20, 40), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(250, 200), Vec2D(20, 40), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(0, 420), Vec2D(400, 20), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(0, 240), Vec2D(20, 200), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(400, 240), Vec2D(20, 200), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(20, 240), Vec2D(150, 20), Vec2D(0, 0)))
borders.append(Border(3000, Vec2D(250, 240), Vec2D(150, 20), Vec2D(0, 0)))

# Single container borders
# borders.append(Border(3000, Vec2D(0, 0), Vec2D(420, 20), Vec2D(0, 0)))
# borders.append(Border(3000, Vec2D(0, 180), Vec2D(420, 20), Vec2D(0, 0)))
# borders.append(Border(3000, Vec2D(0, 20), Vec2D(20, 180), Vec2D(0, 0)))
# borders.append(Border(3000, Vec2D(400, 20), Vec2D(20, 180), Vec2D(0, 0)))

# Particle Generations ---------------------------------------------------------------->

for i in range(50):
    particles.append(Particle(1,
                      Vec2D(
                        random.randint(35, 185),
                        random.randint(35, 185)),
                      Vec2D(
                        random.randint(-10000, 10000),
                        random.randint(-10000, 10000)),
                      Vec2D(10, 10),
                      (255, 0, 0)
                      ))
    particles.append(Particle(1,
                      Vec2D(
                        random.randint(225, 375),
                        random.randint(35, 185)),
                      Vec2D(
                        random.randint(-10000, 10000),
                        random.randint(-10000, 10000)),
                      Vec2D(10, 10),
                      (255, 255, 0)
                      ))

# determine some constants
C = 1
loss = 0.9997
spawnpoint = Vec2D(200, 100)
fps_counter = 0
fps_list = []

while True:
    # fill screen and reset variables for current frame
    screen.fill((5, 5, 5))
    blacklist = []
    Q = Vec2D(0, 0)
    
    # display heat regions
    for heat_region in heat_regions:
        heat_region.update(1/fps)
        k = heat_region.colour_const
        surf = pygame.Surface(heat_region.size.vec)
        res = heat_region.energy_reserve
        surf.fill((min(abs(res)*int(res >= 0)*k, 100), 0, min(abs(res)*int(res <= 0)*k, 100)))
        screen.blit(surf, heat_region.pos.vec, special_flags=pygame.BLEND_RGBA_ADD)
    
    # display detectors
    for detector in detector_regions:
        dsurf = pygame.Surface(detector.size.vec)
        dsurf.fill((100, 100, 100))
        screen.blit(dsurf, detector.pos.vec, special_flags=pygame.BLEND_RGBA_ADD)

    # particle updates
    for i in range(len(particles)):
        
        # update particles
        particles[i].updatePos(1/fps, blacklist, borders, particles, heat_regions, detector_regions, i, C, loss)
        Q = Q + particles[i].e_k
        blacklist.append(i)

        # Debug -->
        # pygame.draw.rect(screen, (0, 255, 0), particle.rect)

        # to rectify problem where drawing a particle off screen on the left created a weird bar
        if not particles[i].pos[0] < 0:
            pygame.draw.circle(screen, particles[i].color, [particles[i].pos[0]+ particles[i].size[0]/2, particles[i].pos[1]+particles[i].size[0]/2], particles[i].size[0]/2)
    
    # finish detector updates(these are located in particle update function)
    for d in detector_regions:
        d.compile_results()
    
    # update borders
    for border in borders:
        border.update(1/fps)
        Q = Q + border.e_k
        pygame.draw.rect(screen, (255, 255, 255), border.rect)
    

    # Original Energy Calc --->
    Q = math.sqrt(Q[0]*Q[0] + Q[1]*Q[1]) / (1_000_000*500) 
    print(round(Q, 3))
    # 1mil is to get mass closer to 1 milligram, 500 is to get the 500x500 pixel box to a point where each pixel is ~0.5 cm
    # The main purpose of this sim is to explore energy change and diffusion in systems, so exact units aren't very important
    
    # iterate fps
    fps_counter += 1
    fps_list.append(fps_counter)
    
    # if the it is the 100th frame, save all the data from this 100 runs
    if fps_counter % 100 == 0:
        for detector in detector_regions:
            savedict = {f"ParticleFlux":detector.flux}
            e_flux = []

            for val in detector.total_energy_flux:
                e_flux.append(round(val, 5))
            
            savedict[f"MagnitudeofEnergyFlux"] = e_flux
            x = []
            y = []
            for i in detector.energy_flux:
                x.append(round(i[0], 5))
                y.append(round(i[1], 5))
            savedict[f"EnergyFluxX"] = x
            savedict[f"EnergyFluxY"] = y
            savedict[f"TimeStep"] = fps_list
            df = pandas.DataFrame(savedict)
            df.to_csv(f"./detector_{detector.id}_data.csv", mode="a", index=False, header=False if fps_list[0] != 1 else True)
            detector.reset()
        fps_list = []

    # quit condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # update display and tick clock
    pygame.display.update()
    clock.tick(60)
