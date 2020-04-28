FROM continuumio/miniconda3

WORKDIR /usr/src/app
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

ENV FLASK_APP=flask_app/__init__.py
RUN python manage.py create_db

EXPOSE 5000
CMD ["gunicorn", "--bind", ":5000", "--workers", "3", "run:app"]
