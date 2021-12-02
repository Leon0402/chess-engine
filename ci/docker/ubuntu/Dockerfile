FROM ubuntu:21.04

ENV TZ=Europe/Berlin
ARG DEBIAN_FRONTEND=noninteractive
ARG APT_FLAGS="--assume-yes --quiet --quiet --allow-unauthenticated --allow-downgrades --allow-remove-essential --allow-change-held-packages"
ARG LATEX_PACKAGES="latexmk texlive-xetex inkscape"
ARG PYTHON_PACKAGES="python3.9 python3-dev python3-pip"
ARG SPHINX_PACKAGES="python3-sphinx texlive-fonts-extra"
RUN apt-get $APT_FLAGS update &&\
    apt-get install $APT_FLAGS apt-utils &&\
    apt-get install $APT_FLAGS git $LATEX_PACKAGES $PYTHON_PACKAGES $SPHINX_PACKAGES &&\
    apt-get clean
