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


from OpenGL.raw.GL.VERSION.GL_1_0 import GL_NONE
import numpy as np

def func1(arr):
    arr[0] = 3.3

arr1 = np.array([1,2,3])
arr2 = np.array([4,5,6])
temp1 = 7
arr3 = np.concatenate((arr1,arr2,temp1), axis=None)

tup = (3,4)
print(tup[1])