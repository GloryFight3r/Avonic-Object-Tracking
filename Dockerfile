FROM balenalib/jetson-nano-ubuntu-python:latest-build

WORKDIR /usr/app

COPY ./src ./src
COPY settings.yaml .
COPY README.md .
COPY pyproject.toml .
COPY run.sh .

RUN apt-get update -y && apt-get upgrade -y --autoremove
RUN apt-get install ffmpeg libsm6 libxext6 -y

# install opencv
RUN apt-get install -y \
build-essential \
cmake \
git \
gfortran \
libatlas-base-dev \
libavcodec-dev \
libavformat-dev \
libcanberra-gtk3-module \
libdc1394-22-dev \
libeigen3-dev \
libglew-dev \
libgstreamer-plugins-base1.0-dev \
libgstreamer-plugins-good1.0-dev \
libgstreamer1.0-dev \
libgtk-3-dev \
libjpeg-dev \
libjpeg8-dev \
libjpeg-turbo8-dev \
liblapack-dev \
liblapacke-dev \
libopenblas-dev \
libpng-dev \
libpostproc-dev \
libswscale-dev \
libtbb-dev \
libtbb2 \
libtesseract-dev \
libtiff-dev \
libv4l-dev \
libxine2-dev \
libxvidcore-dev \
libx264-dev \
pkg-config \
python3-dev \
python3-numpy \
python3-matplotlib \
qv4l2 \
v4l-utils \
zlib1g-dev

RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.7.0.zip && \
    wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.7.0.zip && \
    unzip opencv.zip && \
    unzip opencv_contrib.zip && \
    mv opencv-4.7.0 opencv && \
    mv opencv_contrib-4.7.0 opencv_contrib && \
    rm opencv.zip && \
    rm opencv_contrib.zip && \
    cd opencv && \
    mkdir build && \
    cd build

RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr \
          -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
          -D EIGEN_INCLUDE_PATH=/usr/include/eigen3 \
          -D WITH_OPENCL=OFF \
          -D WITH_CUDA=ON \
          -D CUDA_ARCH_BIN=5.3 \
          -D CUDA_ARCH_PTX="" \
          -D WITH_CUDNN=ON \
          -D WITH_CUBLAS=ON \
          -D ENABLE_FAST_MATH=ON \
          -D CUDA_FAST_MATH=ON \
          -D OPENCV_DNN_CUDA=ON \
          -D ENABLE_NEON=ON \
          -D WITH_QT=OFF \
          -D WITH_OPENMP=ON \
          -D BUILD_TIFF=ON \
          -D WITH_FFMPEG=ON \
          -D WITH_GSTREAMER=ON \
          -D WITH_TBB=ON \
          -D BUILD_TBB=ON \
          -D BUILD_TESTS=OFF \
          -D WITH_EIGEN=ON \
          -D WITH_V4L=ON \
          -D WITH_LIBV4L=ON \
          -D OPENCV_ENABLE_NONFREE=ON \
          -D INSTALL_C_EXAMPLES=OFF \
          -D INSTALL_PYTHON_EXAMPLES=OFF \
          -D PYTHON3_PACKAGES_PATH=/usr/lib/python3/dist-packages \
          -D OPENCV_GENERATE_PKGCONFIG=ON \
          -D BUILD_EXAMPLES=OFF ..
RUN make -j 8
RUN rm -r /usr/include/opencv4/opencv2 && \
    make install && \
    ldconfig && \
    make clean && \
    apt-get -y update

RUN pip install -e '.[prod]'

ENV SERVER_ADDRESS=127.0.0.1:8000
EXPOSE 8000

CMD ./run.sh jetson