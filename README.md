
# 32lidar_imu_fastlio2_gazebo_sim

Gazebo simulation for 32-line LiDAR-IMU fusion SLAM based on FAST‑LIO2 (under development)

​**当前进度：仅完成 Gazebo 传感器仿真，未接入 FAST‑LIO2 建图，可在 RViz 查看 32 线激光雷达点云与 IMU 数据**​。

---

## 一、仿真环境

- Ubuntu 20.04系统
- ROS Noetic版本

## 二、代码结构

代码主要存在两个包里面

- 1.```myrobot_description```包中保存着仿真的机器人模型
- 2.```myrobot```包中包含了世界模型，打开地图的launch文件以及移动障碍物的脚本启动文件

## 三、开源项目参考

- 本实验基于```turtlebot3```实验包完成的，因此需要先自行安装```turtlebot3```相关实验包，这里提供一个安装教程网址：[Turtlebot3入门教程](https://zhuanlan.zhihu.com/p/475365929)
- 本实验代码还参考了Turtlebot迎宾机器人的设计思路，参考的项目代码仓库在：[https://github.com/SEUZTh/welRbot/tree/smach_state](https://github.com/SEUZTh/welRbot/tree/smach_state)
- FAST‑LIO2 激光雷达‑IMU紧耦合SLAM官方开源项目：[https://github.com/hku-mars/FAST_LIO](https://github.com/hku-mars/FAST_LIO)

## 四、测试

### 1、在终端启动launch文件

```
cd ~/catkin_ws
source devel/setup.bash
roslaunch myrobot myhouse_world.launch
```

启动成功可以看到Gazebo中加载出世界环境和小车，小车发射32线可视化射线，Rviz中出现3D雷达点云。

### 2、添加可移动障碍物

```
cd ~/catkin_ws
source devel/setup.bash
rosrun myrobot moving_cylinder.py
```

启动成功可以看到Gazebo出现一个直线往返运动的红色圆柱体障碍物，参数可以在moving_cylinder.py中修改
<img width="2559" height="1209" alt="e6908578e9d9968fb18f53685fba88bc" src="https://github.com/user-attachments/assets/823d63b8-da2c-4d95-974c-c54f1d300b92" />


### 3、启动键盘控制

```
roslaunch turtlebot3\_teleop turtlebot3\_teleop\_key.launch
```

## 五、说明

本人仍在持续学习，技术能力有限，本项目仓库代码会不断迭代更新，目前仅完成 Gazebo 传感器仿真部分，后续将逐步接入 FAST‑LIO2 实现 SLAM 建图定位。如有不足，欢迎交流指正。
