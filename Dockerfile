FROM ubuntu:bionic

RUN apt-get -y update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
   python3-pip \
   python3-gi \
   python-gi-dev

RUN pip3 install --upgrade pip 
RUN pip3 install kafka-python

ENV PYTHONPATH "${PYTHONPATH}:/usr/local/lib/python3.6/dist-packages/"
COPY files/ /
CMD ["/scripts/do_run"]
