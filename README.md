# SimpleTracking
Simple object tracking based on constant acceleration cinematic model and Kalman filtering.

## Prerequisites
* [ROS](http://wiki.ros.org/Installation/Ubuntu)
* [Catkin](http://docs.ros.org/melodic/api/catkin/html/user_guide/installation.html)

## Installation
`git clone --recursive https://github.com/mihaigalos/SimpleTracking.git`

## Building
```
cd SimpleTracking
catkin init
catkin build
```
## Running
```
roscore &
source devel/setup.zsh
python src/tracking.py
```
Fire up rviz with `rviz &`. Now click on `Add` and add a new `Marker`. The tracker automatically
publishes on `/visualization_marker`, so no need to adjust anything. You should see a moving green box
and over it, the predicted position for it, in a dark semi-transparent cube.

## Screenshot
![alt text](screenshots/tracking_screenshot.png)
