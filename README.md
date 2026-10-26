# Cold Case

A Django web app for detectives working on unsolved cases. It keeps track of case files, suspects, their alibis and the evidence collected for each case.

The interface is in Bulgarian.

## Features

- Create, view, edit and delete case files
- Filter and sort the case list
- Case numbers are generated automatically (e.g. `CC-2026-0001`)
- Statuses: open, solved, frozen
- Suspects can be linked to several cases
- Alibis are checked for contradictions: a suspect can't be in two different places at the same time
- Evidence can point to a suspect

## Tech

- Python 3
- Django 6
- SQLite
- HTML and CSS with Django templates

## Running locally

```bash
git clone https://github.com/alexandrabuyuklieva/coldcase.git
cd coldcase
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

## Project structure

- `cases` – case files
- `suspects` – suspects and alibis
- `evidence` – evidence for each case
- `common` – home page, shared models and validators
