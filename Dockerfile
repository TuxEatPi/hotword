FROM python:3.6-stretch

RUN apt-get update && apt-get install -y git gcc python3-dev musl-dev portaudio19-dev make swig g++ libatlas-base-dev

COPY requirements.txt /opt/requirements.txt
COPY test_requirements.txt /opt/test_requirements.txt
RUN pip install -r /opt/requirements.txt

RUN mkdir /workdir

WORKDIR /opt
COPY Makefile /opt/Makefile
RUN mkdir -p /opt/tuxeatpi_hotword_kittai/libs
RUN make dev-build-snowboy

COPY setup.py /opt/setup.py
COPY tuxeatpi_hotword_kittai /opt/tuxeatpi_hotword_kittai
RUN python /opt/setup.py install

WORKDIR /workdir

COPY dialogs /dialogs
COPY intents /intents

ENTRYPOINT ["tep-hotword-kittai", "-w", "/workdir", "-I", "/intents", "-D", "/dialogs"]
