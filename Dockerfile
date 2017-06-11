FROM resin/rpi-raspbian:latest

# Install OS dependencies
RUN apt-get update
RUN apt-get install -qy python3 python3-pip git build-essential python3-dev pkg-config python3-dbus \
libdbus-1-dev libical-dev libreadline-dev bluetooth bluez blueman libbluetooth-dev libdbus-glib-1-dev \
bluetooth bluez blueman libbluetooth-dev python3-gi dbus
RUN apt-get install -qy dbus-x11
# For bluez source compilation
#RUN apt-get install automake libtool libudev-dev

# Install Python dependencies
RUN mkdir /opt/code
WORKDIR /opt/code
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
COPY requirements_test.txt requirements_test.txt
RUN pip3 install -r requirements_test.txt

# Copy source code and execute tests
COPY bluefang /opt/code/bluefang
COPY tests /opt/code/tests
COPY scripts /opt/code/scripts
#USER root

#RUN python3 -m pytest
