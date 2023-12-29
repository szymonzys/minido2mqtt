ARG BUILD_FROM
FROM $BUILD_FROM


LABEL \
  io.hass.version="VERSION" \
  io.hass.type="addon" \
  io.hass.arch="armhf|aarch64|i386|amd64"

ARG TEMPIO_VERSION BUILD_ARCH

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 \
    py3-pip

# So let's set it to our add-on persistent data directory.
WORKDIR /data

# Copy pip requirements for add-on
COPY requirements.txt ./

RUN python3 -m venv /venv

RUN source /venv/bin/activate && \ 
	pip install --no-cache-dir -r requirements.txt

# Copy python scripts for add-on
COPY *.py /

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]