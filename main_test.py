# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# import numpy as np
# import matplotlib.animation as animation

# # plt.plot([1,2,3,4])

# xmin = 0.
# xmax = 25.
# ymin = 0.
# ymax = 25.
# zmin = 0.
# zmax = 25.

# def update_point(frame, data, point, line):
#     print(frame)
#     point.set_data(data[0,:frame],data[1,:frame])
#     point.set_3d_properties(data[2,:frame])
#     line.set_data(data[0,:frame],data[1,:frame])
#     line.set_3d_properties(data[2,:frame])

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.set_xlabel('X')
# ax.set_xlim3d([xmin, xmax])
# ax.set_ylabel('Y')
# ax.set_ylim3d([ymin, ymax])
# ax.set_zlabel('Z')
# ax.set_zlim3d([zmin, zmax])
# ax.set_title('MotionViewer')

# data = np.empty((3,25))
# for i in range(25):
#     v = i * 1
#     data[:,i] = np.array([v,v,v])


# point = ax.plot([],[],[],'bo')[0]
# line = ax.plot([],[],[],'r-')[0]
# line2 = ax.plot([1,2],[1,2],[1,2],'g-')[0]
# line3 = ax.plot([3,4],[3,4],[3,4],'r-')[0]
# # point_ani = animation.FuncAnimation(fig, update_point, frames=25, fargs=(data,point,line),interval=50,blit=False)
# plt.show()



import numpy as np
from utility import Utility as uti

def ZYXEulerToRotMat(euler):
    zang, yang, xang = euler
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    return Rz @ Ry @ Rx

euler1 = np.array([-1.,1.,0.])*np.radians(90)
euler2 = np.array([-1.,1.,0.])*np.radians(90) 
R1 = ZYXEulerToRotMat(euler1)
R2 = ZYXEulerToRotMat(euler2)

R = R1.T @ R2
print(R)