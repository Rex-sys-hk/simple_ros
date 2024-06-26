import numpy as np
import math

def quart_to_rpy_wxyz(w, x, y, z):
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(2 * (w * y - x * z))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (z * z + y * y))
    return [roll, pitch, yaw]

def quart_to_rpy_xyzw(x, y, z, w):
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(2 * (w * y - x * z))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (z * z + y * y))
    return [roll, pitch, yaw]

def rpy2quaternion(roll, pitch, yaw):
    x=np.sin(pitch/2)*np.sin(yaw/2)*np.cos(roll/2)\
        +np.cos(pitch/2)*np.cos(yaw/2)*np.sin(roll/2)
    y=np.sin(pitch/2)*np.cos(yaw/2)*np.cos(roll/2)\
        +np.cos(pitch/2)*np.sin(yaw/2)*np.sin(roll/2)
    z=np.cos(pitch/2)*np.sin(yaw/2)*np.cos(roll/2)\
        -np.sin(pitch/2)*np.cos(yaw/2)*np.sin(roll/2)
    w=np.cos(pitch/2)*np.cos(yaw/2)*np.cos(roll/2)\
        -np.sin(pitch/2)*np.sin(yaw/2)*np.sin(roll/2)
    return x, y, z, w

import rospy
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32MultiArray
from tf import TransformListener
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker, MarkerArray
import tf2_ros
import geometry_msgs.msg

class ROS_INTERFACE:
    def __init__(self, node_name = 'rosbase', anonymous = False, rate = 10):

        rospy.init_node(node_name, anonymous=anonymous)
        # rospy.spin()
        self.rate = rospy.Rate(rate)
        self.tf_listener = TransformListener(True, rospy.Duration(2.0))

        self.publisher = {}
        self.subscriber = {}


    def get_tf(self, source, target, time = rospy.Time(0), eular_angle = True):
        # try:
        (trans, rot) = self.tf_listener.lookupTransform(source, target, time)
        if eular_angle:
            erot = quart_to_rpy_xyzw(*rot)
        return trans, erot
        # except:
        #     print('tf not found')
        #     pass
            # return [0,0,0],[0,0,0,0]
    def publish_tf(self, base_link, child_link, tf):
        # 初始化ROS节点
        rospy.init_node('tf_broadcaster')

        # 创建一个TransformBroadcaster对象
        br = tf2_ros.TransformBroadcaster()

        # 设置发布频率
        rate = rospy.Rate(10.0)  # 10 Hz

        while not rospy.is_shutdown():
            # 创建一个TransformStamped对象
            t = geometry_msgs.msg.TransformStamped()

            # 设置TransformStamped的头部信息
            t.header.stamp = rospy.Time.now()  # 设置时间戳
            t.header.frame_id = base_link    # 设置父坐标系
            t.child_frame_id = child_link   # 设置子坐标系

            # 设置变换矩阵（这里使用单位矩阵作为示例）
            t.transform.translation.x = tf[0]
            t.transform.translation.y = tf[1]
            t.transform.translation.z = tf[2]
            t.transform.rotation.x = tf[3]
            t.transform.rotation.y = tf[4]
            t.transform.rotation.z = tf[5]
            t.transform.rotation.w = tf[6]

            # 发布TransformStamped对象
            br.sendTransform(t)

            # 等待直到下一个循环
            rate.sleep()
    
    def add_tf_broadcaster(self, base_link, child_link, tf):
        import threading
        t = threading.Thread(target=self.publish_tf, args=(base_link, child_link, tf))
        t.start()

    def add_subscriber(self, topic, msg_type, callback, args_dic:dict, queue_size = 10):
        self.subscriber[topic] = rospy.Subscriber(topic, msg_type, callback, args_dic, queue_size = queue_size)

    def add_publisher(self, topic, msg_type, queue_size = 10):
        self.publisher[topic] = rospy.Publisher(topic, msg_type, queue_size = queue_size)
    
    def publish(self, topic, msg):
        self.publisher[topic].publish(msg)

    def make_marker_array(self, seq, frame_id='world', ns='my_namespace', m_type=Marker.ARROW, action=Marker.ADD, scale=[0.05, 0.05, 0.], color=[1.0, 1.0, 1.0, 1.0]):
        """
        seq: Nx6 array, each row is [x, y, z, roll, pitch, yaw]
        color: [r, g, b, a]
        """
        ma = MarkerArray()
        for i,p in enumerate(seq):
            marker = Marker()
            marker.id = i
            marker.header.frame_id = frame_id
            marker.header.stamp = rospy.Time.now()
            marker.ns = ns
            marker.type = m_type
            marker.action = action
            marker.pose.position.x = p[0]
            marker.pose.position.y = p[1]
            marker.pose.position.z = p[2]
            # r = Rotation.from_euler('xyz', p[3:5], degrees=False)
            # q = r.as_quat()
            q = rpy2quaternion(p[3], p[4], p[5])
            marker.pose.orientation.x = q[0]
            marker.pose.orientation.y = q[1]
            marker.pose.orientation.z = q[2]
            marker.pose.orientation.w = q[3]
            marker.scale.x = scale[0]
            marker.scale.y = scale[1]
            marker.scale.z = scale[2]
            marker.color.r = color[0]
            marker.color.g = color[1]
            marker.color.b = color[2]
            marker.color.a = color[3]
            ma.markers.append(marker)

        return ma
