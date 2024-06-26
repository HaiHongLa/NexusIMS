FROM ims-base

COPY ./sampleData/ /sampleData/

RUN pip3 install faker
RUN apt-get install python3-dev gcc


# Keep container running
CMD sh -c "tail -f /dev/null"