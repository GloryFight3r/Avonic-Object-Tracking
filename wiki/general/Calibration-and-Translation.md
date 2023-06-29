This page is about the various assumptions we decided to make,
and how we plan to implement everything.

# Assumptions

To make the project feasible, we decided to assume a few things.
This is mainly due to the largest, overarching problem with the project:
*The [microphone](./wiki/general/Names-and-Conventions.md) does not
provide us with a distance to the speaker*.

Due to this combined with the fact that the microphone array is in a separate position from
the camera, finding out where the speaker is actually located becomes impossible without
hacking/reverse-engineering it, since we do not have access to each individual microphone
within the array. This means that we need to make assumptions about the environment of the room:

1. The room has a flat, horizontal floor
2. The people in the room are of similar height
3. The microphone is installed parallel to the floor
4. The ceiling microphone is oriented in a certain way relative to the camera's home position

With these four points, finding out the rough position of the speaker is rather simple,
since we can intersect the ray (vector) given to us by the microphone with the plane
we calculate during calibration.

That plane is referred to as the [**speaker plane**](./wiki/general/Names-and-Conventions.md).

# Calibration

During the calibration stage, we calculate the distance from the camera to
the microphone and obtain the camera's relative coordinates to the microphone.

To achieve this, the microphone's height
(above the [speaker plane](./wiki/general/Names-and-Conventions.md))
is first set via an input field inside the WebUI or using the
[`/microphone/height` API endpoint](./wiki/general/web-ui/Microphone-endpoints.md).
Then, a person is sent into the room, they direct the camera at themselves and speak.
The direction obtained from the camera and microphone combined with
the microphone's height is enough to calculate all of
the speaker plane's properties and 3D position. In the following two illustrations, there are three points - $C$, $A$, $M$ - which stand for the Camera, Speaker and Microphone respectively.

![2D illustration](../images/calibration_2d.png)
![3D illustration](../images/calibration_3d.jpg)

If we have $h$, the height, which we do, we can calculate the length of the vector $\vec{MA}$.
Since we know the angles at points $C$ and $M$ in addition to that length,
we can derive every side-length of $\triangle{CAM}$ from that information,
which includes $|CM|$. We have just found the length of a ray, which means we have a vector,
and therefore also the coordinates of the camera relative to the microphone.

# Translation

Having calibrated the software, we can now start using it.
The algorithm for translation knowing the speaker's precise position on the plane is simple -
the ray coming from the microphone is intersected with the speaker plane to get
the coordinates of the speaker, and the camera is directed towards that point.
The second step is simple since the relative position of the camera is known.
