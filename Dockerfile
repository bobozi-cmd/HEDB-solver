FROM ubuntu:22.04
ENV TZ Asia/Shanghai
ENV LANG zh_CN.UTF-8

# set domestic source
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN apt-get -qq update \
	&& apt-get -qq -y upgrade \
	&& apt-get -qq install --no-install-recommends build-essential \
	&& apt-get -qq install --no-install-recommends openssh-server \
	&& apt-get -qq install --no-install-recommends sudo \
	&& apt-get -qq install --no-install-recommends vim tmux python3-pip python-dev-is-python3 \
	&& apt-get -qq install --no-install-recommends cmake \
	&& apt-get -qq install --no-install-recommends libmbedtls-dev \
	&& DEBIAN_FRONTEND=nointeractive apt-get -qq install --no-install-recommends postgresql \
	&& apt-get -qq install --no-install-recommends postgresql-contrib \
	&& apt-get -qq install --no-install-recommends postgresql-server-dev-all \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple tqdm z3-solver
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple psycopg2

RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 ubuntu
RUN echo 'ubuntu:1234' | chpasswd
RUN service ssh start
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

RUN service postgresql restart
WORKDIR /home/ubuntu
# COPY --chown=ubuntu:ubuntu ./HEDB ./HEDB

VOLUME [ "/home/ubuntu/HEDB-solver" ]

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]