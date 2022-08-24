
the camera we are using uses the Imaging Control (IC) library, which is written in C++
See https://www.theimagingsource.com/support/documentation/
Imaging Control C++

There is a python wrapper for this here:
https://github.com/TheImagingSource/IC-Imaging-Control-Samples/tree/master/Python

For the python package there are two supported options
* Python NET (.NET via pythonnet https://pythonnet.github.io)
* tisgrabber (C via ctypes)

The latter uses ctp

Of the two, the ctypes version integration is likely faster, though there is not going to be a substantial difference.

