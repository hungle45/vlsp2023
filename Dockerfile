FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

# Setup environments
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Ho_Chi_Minh

RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg locales git apt-utils && \
  apt-get -y install --no-install-recommends python3 python3-pip python3-dev build-essential && \
  apt -y install make cmake gcc g++ && \
  apt -y install libsndfile1-dev espeak && \  
  pip3 install --upgrade pip && \
  locale-gen en_US.UTF-8  && \
  rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY  ./requirements.txt /requirements.txt
RUN   pip3 install -r /requirements.txt && \
	  rm -rf /root/.cache/pip

COPY . /vlsp/

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR /vlsp/backend/

ENTRYPOINT ["python3", "main.py"]
