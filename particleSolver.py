import numpy as np
import particleSystem
from utility import Utility as uti

class ParticleSolver:
    def __init__(self, particleSystem):
        self.particleSystem = particleSystem
    
    def gravity(self):
        g = 9.8
        for i in range(self.particleSystem.particle_num):
            m = self.particleSystem.particles[i][9]
            gv = np.array([0., -m*g, 0.])
            self.particleSystem.particles[i][6:9] += gv

    def dampedSpring(self, dampingData):
        a_index = dampingData.particle_nums[0]
        b_index = dampingData.particle_nums[1]
        a_pos = self.particleSystem.particles[a_index][0:3]
        b_pos = self.particleSystem.particles[b_index][0:3]
        a_vel = self.particleSystem.particles[a_index][3:6]
        b_vel = self.particleSystem.particles[b_index][3:6]

        delta_x = a_pos - b_pos
        delta_x_l2norm = uti.l2norm(a_pos-b_pos)
        delta_v = a_vel - b_vel

        force_a_scalar = dampingData.ks * (delta_x_l2norm-dampingData.rest_length) + dampingData.kd * (np.dot(delta_v,delta_x)/delta_x_l2norm)
        if delta_x_l2norm == 0.:
            force_a = np.zeros(3)
        else:
            force_a = -(force_a_scalar/delta_x_l2norm) * delta_x
        force_b = -force_a

        m_a = self.particleSystem.particles[a_index][9]
        m_b = self.particleSystem.particles[b_index][9]
        self.particleSystem.particles[a_index][6:9] += m_a * force_a
        self.particleSystem.particles[b_index][6:9] += m_b * force_b

    def applyForce(self, dampingDataSet):
        # initialize
        for i in range(self.particleSystem.particle_num):
            self.particleSystem.particles[i][6:9] = np.zeros(3)

        # gravity
        self.gravity()

        # damped spring
        for dampingData in dampingDataSet:
            self.dampedSpring(dampingData)
        
        # friction

    @staticmethod
    def collisionCheck(particle, normal_v):
        x_threshold = 1.0e-5
        x = np.array(particle[0:3])
        v = np.array(particle[3:6])
        check1 = None
        check2 = None
        if np.dot(x, normal_v) < x_threshold:
            check1 = True
        else:
            check1 = False
        
        if np.dot(v, normal_v) < 0.:
            check2 = True
        else:
            check2 = False
        
        if check1 and check2:
            return True
        else:
            return False
    
    @staticmethod
    def collisionResponse(particle, normal_v):
        # 탄성계수
        kr = 1.0
        v = np.array(particle[3:6])
        Nnormal_v = uti.normalized(normal_v)
        v_n = np.dot(v, normal_v) * Nnormal_v
        v_t = v - v_n
        
        new_v_n = -kr * v_n
        particle[3:6] = new_v_n + v_t

    @staticmethod
    def contactCheck(particle, normal_v):
        # x_threshold = 1.0e-10
        x_threshold = 1.0e-5
        v_threshold = 1.0e-10
        x = np.array(particle[0:3])
        v = np.array(particle[3:6])
        check1 = None
        check2 = None
        if np.dot(x, normal_v) < x_threshold:
            check1 = True
        else:
            check1 = False
        
        if np.abs(np.dot(v, normal_v)) < v_threshold:
            check2 = True
        else:
            check2 = False
        
        if check1 and check2:
            return True
        else:
            return False

    @staticmethod
    def contactResponse(particle, normal_v):
        f = np.array(particle[6:9])
        Nnormal_v = uti.normalized(normal_v)
        f_n = np.dot(f, Nnormal_v) * Nnormal_v
        particle[6:9] = f - f_n

    def calDerivative(self, dampingDataSet, normal_v):
        # apply force
        self.applyForce(dampingDataSet)

        # contact, collision check
        for particle in self.particleSystem.particles:
            if ParticleSolver.contactCheck(particle, normal_v):
                ParticleSolver.contactResponse(particle, normal_v)
                continue
            if ParticleSolver.collisionCheck(particle, normal_v):
                ParticleSolver.collisionResponse(particle, normal_v)

        # calculate derivative
        x_derivative = []
        v_derivative = []
        for particle in self.particleSystem.particles:
            x_derivative.append(np.array(particle[3:6]))
            v_derivative.append(1/particle[9] *np.array(particle[6:9]))
        
        return x_derivative, v_derivative

    def eulerIntegration(self, timestep, dampingDataSet, normal_v):
        x_derivative,v_derivative = self.calDerivative(dampingDataSet, normal_v)

        for particle,x_d,v_d in zip(self.particleSystem.particles,x_derivative,v_derivative):
            particle[0:3] = particle[0:3] + timestep * x_d
            particle[3:6] = particle[3:6] + timestep * v_d
        
        self.particleSystem.time += timestep
        
    
            

