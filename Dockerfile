FROM python:3.10-slim-buster as builder

COPY . .

# WORKDIR .

# COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
# RUN pip install poetry
# RUN poetry config virtualenvs.in-project true
# RUN poetry shell
# RUN poetry install

EXPOSE 8000

CMD ["python",  "main.py"]