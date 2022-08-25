FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN pip install poetry==1.1.7 && \
    poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry install --no-interaction --no-ansi

COPY . /code/