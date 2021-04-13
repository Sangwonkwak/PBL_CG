import numpy as np

def l2norm(v):
        return np.sqrt(np.dot(v, v))

def normalized(v):
        l = l2norm(v)
        if l == 0.:
            return np.zeros(3)
        return 1/l * np.array(v)

def cal_angleByDot(a, b, c):
        ab = b - a
        ac = c - a
        ab_len = l2norm(ab[:-1])
        ac_len = l2norm(ac[:-1])
        up = np.dot(ab,ac)
        down = ab_len * ac_len
        x = up / down
        if x > 1.:
            x = 1.
        elif x < -1.:
            x = -1.
        return np.arccos(x)

def exp(rv):
        M = np.identity(4) 
        u = normalized(rv)
        a = l2norm(rv)
        R = np.array([[np.cos(a)+u[0]*u[0]*(1-np.cos(a)), u[0]*u[1]*(1-np.cos(a))-u[2]*np.sin(a), u[0]*u[2]*(1-np.cos(a))+u[1]*np.sin(a)],
                    [u[1]*u[0]*(1-np.cos(a))+u[2]*np.sin(a), np.cos(a)+u[1]*u[1]*(1-np.cos(a)), u[1]*u[2]*(1-np.cos(a))-u[0]*np.sin(a)],
                    [u[2]*u[0]*(1-np.cos(a))-u[1]*np.sin(a), u[2]*u[1]*(1-np.cos(a))+u[0]*np.sin(a), np.cos(a)+u[2]*u[2]*(1-np.cos(a))]
                    ])
        M[:-1, :-1] = R
        return M

def main():
    # local_frame = np.array([[2,7,5,3],[3,8,2,3],[1,9,1,1],[0,0,0,1]])
    # a = np.array([3, 3, 1, 1.])
    # b = np.array([2, 5, 6, 1.])
    # c = np.array([7, -1, 1, 1.])
    # ###1st method
    # ab = b - a
    # ac = c - a
    # a_rv = np.cross(ab[:-1],ac[:-1])
    # a_rv_len = l2norm(a_rv)
    # theta = cal_angleByDot(a, b, c)
    # a_rv /= a_rv_len
    # a_rv *= theta
    
    # a_rv_temp = np.zeros(4)
    # a_rv_temp[:-1] = a_rv
    # a_rv1 = np.linalg.inv(local_frame) @ a_rv_temp
    # a_rm1 = exp(a_rv1[:-1])
    # frame1 = local_frame @ a_rm1

    # ###2nd method
    # a_rm2 = exp(a_rv)
    # frame2 = a_rm2 @ local_frame

    # print(frame1)
    # print(frame2)
    # for i in range(9,-1,-1):
    #     print(i)
    # arr1 = np.array([1,2,3,4])
    # arr2 = arr1
    # arr2[0] = 123
    arr1 = np.identity(4)
    print(arr1)

if __name__ == "__main__":
    main()