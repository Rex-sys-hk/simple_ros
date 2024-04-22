# simple_ros

A toy ros interface that is easy to use, avoiding repetitive work like creating MarkerArray.

Don't forget to install rospy with commands
`sudo pip3 install rospkg catkin_pkg`

All Contents Inside
```
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

```
