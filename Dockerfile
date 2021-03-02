FROM python:3

WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/abenassi/Google-Search-API
EXPOSE 5000
CMD ["python", "app.py"]