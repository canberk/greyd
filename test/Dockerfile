FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./

# pip upgrade
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

# -r means "short test summery info" and -a is "all except pass"
CMD [ "pytest", "-ra", "./tests.py" ]
