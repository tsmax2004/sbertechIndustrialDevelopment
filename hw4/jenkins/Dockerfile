FROM jenkins/jenkins:lts
USER root

RUN apt-get update  \
    && apt-get install -y python3 python3-pip libpq-dev bash maven ansible openssh-client sshpass \
    && pip install --no-cache-dir --break-system-packages pytest pytest-mock allure-pytest pytest-cov

CMD ["/usr/local/bin/jenkins.sh"]
