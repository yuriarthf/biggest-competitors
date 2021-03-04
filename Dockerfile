FROM python:3

WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
VOLUME output
CMD ["python", "app.py"]