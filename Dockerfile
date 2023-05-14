FROM python:3.11.3-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
  sudo \
  vim \
  curl \
  git \
  unzip \
  build-essential \
  jq \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

RUN ipython profile locate default
COPY ./ipython_startup.py /root/.ipython/profile_default/startup/

RUN mkdir /usr/local/share/jupyter/lab/settings
COPY ./jupyterlab_overrides.json /usr/local/share/jupyter/lab/settings/overrides.json

EXPOSE 8888

CMD ["jupyter-lab", ".", "--ip", "0.0.0.0", \
  "--port", "8888", "--no-browser", "--allow-root"]
