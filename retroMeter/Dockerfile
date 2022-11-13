# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

# Copy root filesystem
COPY rootfs /

RUN apk add --no-cache python3 py3-pip py3-smbus py3-paho-mqtt 
RUN pip3 install python3-json numpy
COPY test.py /
COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]