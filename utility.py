import numpy as np

class Utility:
    @staticmethod
    def l2norm(v):
        return np.sqrt(np.dot(v, v))

    @staticmethod
    def normalized(v):
        l = l2norm(v)
        return 1/l * np.array(v)

    @staticmethod
    def lerp(v1, v2, t):
        return (1-t)*v1 + t*v2

    @staticmethod
    def exp(rv):
        u = normalized(rv)
        a = l2norm(rv)
        R = np.array([[np.cos(a)+u[0]*u[0]*(1-np.cos(a)), u[0]*u[1]*(1-np.cos(a))-u[2]*np.sin(a), u[0]*u[2]*(1-np.cos(a))+u[1]*np.sin(a)],
                    [u[1]*u[0]*(1-np.cos(a))+u[2]*np.sin(a), np.cos(a)+u[1]*u[1]*(1-np.cos(a)), u[1]*u[2]*(1-np.cos(a))-u[0]*np.sin(a)],
                    [u[2]*u[0]*(1-np.cos(a))-u[1]*np.sin(a), u[2]*u[1]*(1-np.cos(a))+u[0]*np.sin(a), np.cos(a)+u[2]*u[2]*(1-np.cos(a))]
                    ])
        return R

    @staticmethod
    def log(R):
        a = np.arccos((R[0][0]+R[1][1]+R[2][2]-1)/2)
        v1 = (R[2][1]-R[1][2])/(2*np.sin(a))
        v2 = (R[0][2]-R[2][0])/(2*np.sin(a))
        v3 = (R[1][0]-R[0][1])/(2*np.sin(a))
        rv = a * np.array([v1,v2,v3])
        return rv

    @staticmethod
    def slerp(R1,R2,t):
        result = R1 @ exp(t*log(R1.T @ R2))
        return result

    # R2는 posture difference
    @staticmethod
    def addByT(R1,R2,t):
        result = R1[:-1,:-1] @ exp(t*log(R2))
        return result