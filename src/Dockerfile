FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./

# pip upgrade
RUN pip install --upgrade pip

# install packages
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "-m", "greyd" ]
