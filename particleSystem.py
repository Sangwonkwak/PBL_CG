import numpy as np

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.particle_num = 0
        self.time = 0
    
    def addParticle(self, particle):
        self.particles.append(particle)
        self.particle_num += 1

class DampingData:
    def __init__(self, ks, kd, particle_nums, rest_length):
        self.ks = ks
        self.kd = kd
        self.particle_nums = particle_nums
        self.rest_length = rest_length