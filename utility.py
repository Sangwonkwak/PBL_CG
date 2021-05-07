import numpy as np

class Utility:
    @staticmethod
    def l2norm(v):
        return np.sqrt(np.dot(v, v))

    @staticmethod
    def normalized(v):
        l = Utility.l2norm(v)
        if l == 0.:
            return np.zeros(3)
        return 1/l * np.array(v)

    @staticmethod
    def lerp(v1, v2, t):
        return (1-t)*v1 + t*v2

    @staticmethod
    def exp(rv):
        u = Utility.normalized(rv)
        a = Utility.l2norm(rv)
        R = np.array([[np.cos(a)+u[0]*u[0]*(1-np.cos(a)), u[0]*u[1]*(1-np.cos(a))-u[2]*np.sin(a), u[0]*u[2]*(1-np.cos(a))+u[1]*np.sin(a)],
                    [u[1]*u[0]*(1-np.cos(a))+u[2]*np.sin(a), np.cos(a)+u[1]*u[1]*(1-np.cos(a)), u[1]*u[2]*(1-np.cos(a))-u[0]*np.sin(a)],
                    [u[2]*u[0]*(1-np.cos(a))-u[1]*np.sin(a), u[2]*u[1]*(1-np.cos(a))+u[0]*np.sin(a), np.cos(a)+u[2]*u[2]*(1-np.cos(a))]
                    ])
        return R

    @staticmethod
    def log(R):
        # if np.trace(R) == 3.0:
        #     return np.zeros(3)
        x = (R[0][0]+R[1][1]+R[2][2]-1)/2
        if x > 1.:
            x = 1.
        elif x < -1.:
            x = -1.
        a = np.arccos(x)
        if np.sin(a) == 0.:
            v1 = 0.
            v2 = 0.
            v3 = 0.
        else:
            v1 = (R[2][1]-R[1][2])/(2*np.sin(a))
            v2 = (R[0][2]-R[2][0])/(2*np.sin(a))
            v3 = (R[1][0]-R[0][1])/(2*np.sin(a))
        # v1 = (R[2][1]-R[1][2])/(2*np.sin(a))
        # v2 = (R[0][2]-R[2][0])/(2*np.sin(a))
        # v3 = (R[1][0]-R[0][1])/(2*np.sin(a))
        rv = a * np.array([v1,v2,v3])
        return rv

    @staticmethod
    def slerp(R1,R2,t):
        result = R1 @ Utility.exp(t*Utility.log(R1.T @ R2))
        return result

    # R2는 posture difference
    @staticmethod
    def addByT(R1,R2,t):
        result = R1 @ Utility.exp(t*Utility.log(R2))
        return result
    
    @staticmethod
    def addByT_v2(R1,R2,t):
        result = Utility.exp(t*Utility.log(R1)) @ R2
        return result
    
    @staticmethod
    def linearFunc(coeff, x):
        return coeff * x
    
    @staticmethod
    def sinFunc(totalF, curF):
        return totalF * np.sin(curF * np.pi * 0.5 * (1./totalF))

    @staticmethod
    def linearFunc_t(slope, x):
        return slope * x
    
    @staticmethod
    def linearFunc2_t(slope, x):
        return 1. - (slope*x)
    
    @staticmethod
    def sinFunc_t(slice, x):
        return np.sin(x * np.pi * 0.5 * (1./slice))
    
    @staticmethod
    def cosFunc_t(slice, x):
        return np.cos(x * np.pi * 0.5 * (1./slice))
    
    @staticmethod
    def projection_y(R):
        rv = Utility.log(R)
        y = np.array([0., 1., 0.])
        val = np.dot(rv, y)
        new_rv = np.array([0., val, 0.])
        new_R = Utility.exp(new_rv)
        return new_R
