FROM resin/rpi-raspbian:latest

# Install OS dependencies
RUN echo "Installing OS package dependencies"
RUN ./scripts/install-linux

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
