cmake_minimum_required(VERSION 3.0.2)
project(myrobot)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY launch world
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
