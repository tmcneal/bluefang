FROM resin/rpi-raspbian:latest

RUN mkdir /opt/code
WORKDIR /opt/code

# Install OS dependencies
RUN echo "Installing OS package dependencies"
COPY scripts /opt/code/scripts
RUN  /opt/code/scripts/install-linux

# For bluez source compilation
#RUN apt-get install automake libtool libudev-dev

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
COPY requirements_test.txt requirements_test.txt
RUN pip3 install -r requirements_test.txt

# Copy source code and execute tests
COPY bluefang /opt/code/bluefang
COPY tests /opt/code/tests
#USER root

#RUN python3 -m pytest
