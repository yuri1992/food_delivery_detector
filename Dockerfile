FROM python:3.7.0

# COPY ["foo","bar","/sef/"]
# Copying application

RUN mkdir /food
COPY . /food
WORKDIR /food

ENV FLASK_APP=server.py
RUN pip install -r requirements.txt
CMD [ "flask", "run", "--host=0.0.0.0" ]