FROM python:3.8
ADD . /app
WORKDIR /app
RUN export DJANGO_SETTINGS_MODULE=oauth_project.settings
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements-dev-actualizado.txt
RUN python3.8 -m pip install gunicorn
RUN python3.8 -m pip install pytest
RUN export DJANGO_SETTINGS_MODULE=oauth_project.settings
RUN export DJANGO_SETTINGS_MODULE=oauth_project.settings
CMD ["export DJANGO_SETTINGS_MODULE=oauth_project.settings"]
EXPOSE 8000
