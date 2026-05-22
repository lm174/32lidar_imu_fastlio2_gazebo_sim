cmake_minimum_required(VERSION 3.0.2)
project(myrobot_description)

find_package(catkin REQUIRED COMPONENTS
  urdf
  xacro
  turtlebot3_description
)

catkin_package(
  CATKIN_DEPENDS urdf xacro turtlebot3_description
)

install(DIRECTORY urdf
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)