from data import *
import numpy as np

class BVH_Parsing:
    def __init__(self):
        # end effector뺀 joint 개수
        self.joint_num = 0
        # end effector포함한 joint 개수
        self.total_joint_num = 0
        self.jointList = []
        self.frames = 0
        self.frame_rate = 0
    
    # Make tree structure for parsing hierarchical model
    def make_tree(self, full_list, parent, line_num, channel_list, bufferIndex):
        while True:
            line = full_list[line_num[0]].lstrip().split(' ')
            if line[0] == "JOINT" or line[0] == "ROOT":
                self.joint_num += 1
                self.total_joint_num += 1
                new_node = Node(line[1].rstrip('\n'))
                # offset
                offset_data = full_list[line_num[0]+2].lstrip().split(' ')
                new_node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                # channel
                channel_data = full_list[line_num[0]+3].lstrip().split(' ')
                for j in range(3):
                    if line[0] == "ROOT":
                        j += 3
                    channel = channel_data[2+j].rstrip('\n')
                    if channel == "XROTATION" or channel == "Xrotation":
                        channel_list.append("X")
                    elif channel == "YROTATION" or channel == "Yrotation":
                        channel_list.append("Y")
                    elif channel == "ZROTATION" or channel == "Zrotation":
                        channel_list.append("Z")

                new_node.parent = parent
                new_node.bufferIndex = bufferIndex[0]
                bufferIndex[0] += 1

                if line[0] != "ROOT":
                    parent.child.append(new_node)
                line_num[0] += 4

                self.jointList.append(new_node)
                self.make_tree(full_list, new_node, line_num, channel_list, bufferIndex)
            elif line[0] == "End":
                self.total_joint_num += 1
                new_node = Node("__END__")
                # offset
                offset_data = full_list[line_num[0]+2].lstrip().split(' ')
                new_node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                
                new_node.parent = parent
                parent.child.append(new_node)
                line_num[0] += 3
                self.jointList.append(new_node)
                self.make_tree(full_list, new_node, line_num, channel_list, bufferIndex)
                
            elif line[0] == '}\n':
                line_num[0] += 1
                return
                
            elif line[0] == "MOTION\n":
                return new_node
            else:
                line_num[0] += 1
        
    def make_postures(self, full_list, start_line_num, channel_list):
        # get frames
        temp_frame= full_list[start_line_num+1].split()
        self.frames = int(temp_frame[1])
        temp_frame_rate = full_list[start_line_num+2].split()
        self.frame_rate = float(temp_frame_rate[2])
        

        line_num = start_line_num + 3
        postures = []
        # start posture
        temp_rmatrix = []
        for num in range(self.joint_num):
            M = np.identity(4)
            temp_rmatrix.append(M)
        temp_origin = [0., 0., 0.]
        postures.append(Posture(temp_origin, temp_rmatrix))

        for i in range(self.frames):
            line = full_list[line_num+i].split(' ')
            if len(line) == 1:
                line = full_list[line_num+i].split('\t')
            # posture = Posture()
            origin = [float(line[0]), float(line[1]), float(line[2])]
            rmatrix = []
            for j in range(self.joint_num):
                M = np.identity(4)
                for k in range(3):
                    R = np.identity(4)
                    channel_value = channel_list[3*j+k]
                    th = np.radians(float(line[3*(j+1)+k]))
                    if channel_value == "X":
                        R[:3,:3] = [[1., 0., 0.],
                                    [0., np.cos(th), -np.sin(th)],
                                    [0., np.sin(th), np.cos(th)]
                                    ]
                    elif channel_value == "Y":
                        R[:3,:3] = [[np.cos(th), 0., np.sin(th)],
                                    [0., 1., 0.],
                                    [-np.sin(th), 0., np.cos(th)]
                                    ]
                    elif channel_value == "Z":
                        R[:3,:3] = [[np.cos(th), -np.sin(th), 0.],
                                    [np.sin(th), np.cos(th), 0.],
                                    [0., 0., 1.]
                                    ]
                    M = M @ R
                
                # posture.Rmatrix.append(M)
                rmatrix.append(M)
            
            rmatrix[0][:-1,3] = origin
            postures.append(Posture(origin, rmatrix))
        #     posture.Rmatrix[0][:-1,3] = origin
        #     posture.origin = origin
        #     postures.append(posture)
        # for i in range(4):
        #     print(postures[i].Rmatrix[0])
        #     print(postures[i].Rmatrix[1])
        #     print(postures[i].origin)
        
        return postures