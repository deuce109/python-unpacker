FROM python

WORKDIR /app

RUN mkdir ./tmp

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENV DATA_PATH /data

COPY ./ ./

ENTRYPOINT [ "flask", "--app", "main", "run",  "--host=0.0.0.0", "--port=5000"  ]