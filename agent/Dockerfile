FROM docker:28-cli@sha256:625d9431a9f54c5a2bc90f24f0e1c3d55b1349fd857dd85035f98c2c9acbdd4d AS docker-cli
FROM jenkins/inbound-agent:3385.vf1123fb_515da_-1-jdk21@sha256:6dbeabd484bb3926293de0b337117f7ad8bb2c0ba1a425b3e34e3d3983b5e1f9
COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
USER jenkins
WORKDIR /home/jenkins/agent
