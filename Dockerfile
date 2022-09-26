FROM python:3
ADD script.py /
RUN pip3 install requests
RUN pip3 install pytelegrambotapi
CMD [ "python" , "-u", "./script.py" ]