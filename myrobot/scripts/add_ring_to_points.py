#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gazebo velodyne 插件不会输出 ring 字段，但 FAST-LIO2 需要它来按扫描线分组点云。
这个节点根据 (x,y,z) 反推每个点属于第几条扫描线（ring），并重新发布点云。
"""
import math
import rospy
import struct
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs import point_cloud2
import ctypes


# 你的32线激光雷达垂直角度参数（从 xacro 文件中获取）
VERTICAL_MIN = -0.535292   # rad
VERTICAL_MAX = 0.186226    # rad
N_SCANS = 32


class AddRingNode:
    def __init__(self):
        rospy.init_node("add_ring_node")

        # 订阅 Gazebo 输出的原始点云
        self.sub = rospy.Subscriber(
            "/points2",
            PointCloud2,
            self.callback,
            queue_size=10,
        )

        # 发布带 ring 字段的点云（使用 FAST-LIO2 默认话题名）
        self.pub = rospy.Publisher(
            "/velodyne_points",
            PointCloud2,
            queue_size=10,
        )

        # 预计算每条线的垂直角度
        self.line_angles = [
            VERTICAL_MIN + i * (VERTICAL_MAX - VERTICAL_MIN) / (N_SCANS - 1)
            for i in range(N_SCANS)
        ]

        rospy.loginfo("add_ring_node started, converting /points2 -> /velodyne_points")

    def callback(self, msg):
        # 解析点云的各字段偏移量
        x_offset = 0
        y_offset = 4
        z_offset = 8
        point_step = msg.point_step

        # 提取所有点的坐标
        rings = []
        for i in range(msg.width * msg.height):
            start = i * point_step
            x = struct.unpack_from("f", msg.data, start + x_offset)[0]
            y = struct.unpack_from("f", msg.data, start + y_offset)[0]
            z = struct.unpack_from("f", msg.data, start + z_offset)[0]

            # 计算垂直角度
            horizontal_dist = math.sqrt(x * x + y * y)
            if horizontal_dist < 1e-6:
                ring = 0
            else:
                vertical_angle = math.atan2(z, horizontal_dist)
                # 查找最近的扫描线
                ring = int(
                    round(
                        (vertical_angle - VERTICAL_MIN)
                        / (VERTICAL_MAX - VERTICAL_MIN)
                        * (N_SCANS - 1)
                    )
                )
                ring = max(0, min(N_SCANS - 1, ring))
            rings.append(ring)

        # 构建新的 PointCloud2，在原字段基础上追加 ring 字段
        fields = list(msg.fields) + [
            PointField(
                name="ring",
                offset=point_step,
                datatype=PointField.UINT16,
                count=1,
            )
        ]

        new_point_step = point_step + 2  # uint16 = 2 bytes
        new_data = bytearray(msg.width * msg.height * new_point_step)

        for i in range(msg.width * msg.height):
            old_start = i * point_step
            new_start = i * new_point_step
            # 复制原始点数据
            new_data[new_start : new_start + point_step] = msg.data[
                old_start : old_start + point_step
            ]
            # 写入 ring 值（uint16）
            struct.pack_into("<H", new_data, new_start + point_step, rings[i])

        new_msg = PointCloud2()
        new_msg.header = msg.header
        new_msg.height = msg.height
        new_msg.width = msg.width
        new_msg.fields = fields
        new_msg.is_bigendian = msg.is_bigendian
        new_msg.point_step = new_point_step
        new_msg.row_step = new_point_step * msg.width
        new_msg.is_dense = msg.is_dense
        new_msg.data = bytes(new_data)

        self.pub.publish(new_msg)


if __name__ == "__main__":
    node = AddRingNode()
    rospy.spin()
