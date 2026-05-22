#!/usr/bin/env python3

import os
import rospy
import rospkg
import math
from gazebo_msgs.srv import SpawnModel, SetModelState
from gazebo_msgs.msg import ModelState
from geometry_msgs.msg import Pose, Point, Quaternion


class MovingCylinder:
    """
    移动圆柱体控制类
    用于在Gazebo中生成并控制一个做直线往返运动的红色圆柱体
    """

    MODEL_NAME = "moving_cylinder"

    # SDF模型文件路径
    SDF_PATH = os.path.join(
        rospkg.RosPack().get_path("myrobot_description"),
        "urdf",
        "moving_cylinder.sdf",
    )

    # 运动参数配置
    LINE_CENTER_X = 0.0
    LINE_Y = 1.5
    LINE_HALF_LENGTH = 0.5
    LINE_SPEED = 0.1
    UPDATE_RATE = 20

    def __init__(self):
        """
        初始化节点和服务代理
        """
        rospy.init_node("moving_cylinder")
        self._spawn_proxy = None
        self._set_state_proxy = None

    def _wait_for_service(self, service_name, timeout):
        """
        等待Gazebo服务可用
        Args:
            service_name: 服务名称
            timeout: 超时时间
        Returns:
            bool: 服务是否可用
        """
        rospy.loginfo("Waiting for %s ...", service_name)
        try:
            rospy.wait_for_service(service_name, timeout=timeout)
        except rospy.ROSException:
            rospy.logerr("Timeout waiting for %s!", service_name)
            return False
        return True

    def _load_sdf(self):
        """
        从文件加载SDF模型描述
        Returns:
            str: SDF模型字符串（已替换模型名称）
        """
        with open(self.SDF_PATH, "r") as f:
            return f.read().format(name=self.MODEL_NAME)

    def spawn(self):
        """
        在Gazebo中生成圆柱体模型
        Returns:
            bool: 生成是否成功
        """
        if not self._wait_for_service("/gazebo/spawn_sdf_model", 30.0):
            return False

        self._spawn_proxy = rospy.ServiceProxy("/gazebo/spawn_sdf_model", SpawnModel)

        init_x = self.LINE_CENTER_X + self.LINE_HALF_LENGTH
        init_y = self.LINE_Y

        sdf = self._load_sdf()
        pose = Pose(
            position=Point(init_x, init_y, 0.0),
            orientation=Quaternion(0, 0, 0, 1),
        )

        try:
            self._spawn_proxy(self.MODEL_NAME, sdf, "", pose, "world")
            rospy.loginfo("Spawned %s at (%.1f, %.1f)", self.MODEL_NAME, init_x, init_y)
        except rospy.ServiceException as e:
            rospy.logerr("Failed to spawn %s: %s", self.MODEL_NAME, e)
            return False
        return True

    def run(self):
        """
        运行直线往返运动控制循环
        """
        if not self._wait_for_service("/gazebo/set_model_state", 10.0):
            return

        self._set_state_proxy = rospy.ServiceProxy("/gazebo/set_model_state", SetModelState)
        rospy.loginfo("Starting straight-line back-and-forth movement...")

        rate = rospy.Rate(self.UPDATE_RATE)
        start_time = rospy.Time.now().to_sec()

        while not rospy.is_shutdown():
            elapsed = rospy.Time.now().to_sec() - start_time

            # 使用正弦函数实现直线往返运动
            x = self.LINE_CENTER_X + self.LINE_HALF_LENGTH * math.sin(self.LINE_SPEED * elapsed)
            y = self.LINE_Y

            # 构造模型状态消息
            state = ModelState()
            state.model_name = self.MODEL_NAME
            state.pose.position.x = x
            state.pose.position.y = y
            state.pose.position.z = 0.0
            state.pose.orientation = Quaternion(0, 0, 0, 1)
            state.reference_frame = "world"

            try:
                self._set_state_proxy(state)
            except rospy.ServiceException as e:
                rospy.logwarn("set_state failed: %s", e)

            rate.sleep()


if __name__ == "__main__":
    cylinder = MovingCylinder()
    if cylinder.spawn():
        rospy.sleep(2.0)
        cylinder.run()
