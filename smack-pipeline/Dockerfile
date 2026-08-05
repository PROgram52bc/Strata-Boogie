FROM --platform=linux/amd64 ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV SMACKDIR=/home/user/smack
# Pin SMACK so the generated Boogie is reproducible. A floating clone drifts with
# SMACK's frontend: newer releases emit control flow (e.g. two-target gotos that
# are not obvious inverses) that the translator does not yet reduce.
ENV SMACK_REF=v2.10.0

RUN apt-get update && \
    apt-get -y install software-properties-common wget sudo g++ git && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m user && \
    echo 'user ALL=(root) NOPASSWD: ALL' >> /etc/sudoers

USER user
WORKDIR /home/user

RUN git clone https://github.com/smackers/smack.git $SMACKDIR && \
    cd $SMACKDIR && git checkout $SMACK_REF

WORKDIR $SMACKDIR

RUN TEST_SMACK=0 bin/build.sh

RUN echo "source /home/user/smack.environment" >> ~/.bashrc

ENTRYPOINT ["/bin/sh", "-c", "exec /bin/bash"]
