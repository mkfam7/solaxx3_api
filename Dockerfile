FROM python:3.11
EXPOSE 8000

WORKDIR /opt/rest_api

COPY . .
SHELL ["/bin/bash", "-c"]
RUN bash setup.sh -nq
RUN pip3 install -r requirements/python3.11/django5.2.txt

RUN chmod +x start.sh
CMD if [ -e .user_created ]; then \
    ./start.sh 0.0.0.0; \
    else ./start.sh --create-user -qf --prestart "touch .user_created" 0.0.0.0; fi
