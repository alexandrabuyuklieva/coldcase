# Cold Case

A Django web app for detectives working on unsolved cases. It keeps track of case files, suspects, their alibis and the evidence collected for each case.

The interface is in Bulgarian.

## Features

- Full CRUD for case files, suspects, alibis and evidence
- Case numbers are generated automatically (e.g. `CC-2026-0001`) and are read-only when editing
- Case statuses: open, solved, frozen
- Searching, filtering, sorting and pagination on every list page
- Suspects can be linked to several cases
- **Suspicion index** - every suspect gets a score based on how much evidence points to them
- **Alibi contradiction check** - a suspect can't claim to be in two different places at the same time
- Evidence can't be dated before the crime and can only implicate suspects linked to the same case
- A suspect can't be removed from a case while there is evidence against them in it
- Confirmation page before every delete, with a warning about what else will be removed
- Success messages after every create, update and delete
- Custom 404 and 500 pages

## Tech

- Python 3.12+
- Django 6
- SQLite
- WhiteNoise (serves the static files when `DEBUG` is off)
- Custom HTML and CSS with Django templates

## Running locally

```bash
git clone https://github.com/alexandrabuyuklieva/coldcase.git
cd coldcase
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

The database starts empty. Everything can be created from the UI: start with **+ Ново досие**, then add suspects and evidence from the case page.

### Environment variables

None are required. The defaults work for local testing.

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_DEBUG` | `False` | Set to `True` to turn on debug mode. With `False` the custom 404 page is shown. |
| `DJANGO_SECRET_KEY` | development key | Secret key. Set your own in production. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hosts. |

### Tests

```bash
python manage.py test
```

## Database

| Model | App | Relationships |
| --- | --- | --- |
| `Case` | `cases` | - |
| `Suspect` | `suspects` | many-to-many with `Case` |
| `Alibi` | `suspects` | many-to-one with `Suspect` |
| `Evidence` | `evidence` | many-to-one with `Case`, many-to-one with `Suspect` (optional) |

All models inherit from the abstract `TimeStampedModel` in `common`, which adds `created_at` and `updated_at`.

Database-level rules:

- an alibi must end after it starts (check constraint)
- evidence confidence can't be over 100% (check constraint)
- case numbers are unique, with an index on case status and crime date for the filtered lists

## Pages

| Page | URL |
| --- | --- |
| Home - statistics and latest open cases | `/` |
| Case list, case details, create, edit, delete | `/cases/` |
| Suspect list, suspect details, create, edit, delete | `/suspects/` |
| Add, edit and delete alibis | from the suspect details page |
| Evidence list, evidence details, create, edit, delete | `/evidence/` |

All pages are reachable from the navigation bar or from links on other pages.

## Forms and validation

- `CaseForm` - the case number is shown as a disabled field when editing
- `SuspectForm` - checkbox list of cases, blocks unlinking a case with implicating evidence
- `AlibiForm` - the suspect is excluded and set from the URL
- `EvidenceForm` / `EvidenceEditForm` - the case can't be changed after the evidence is created
- Filter forms for the three list pages, built on the shared `SortableFilterForm`

All forms have custom labels, help texts, placeholders and error messages. Validation lives in:

- `common/validators.py` - reusable validators (no future dates, case number format)
- model `clean()` methods - rules that depend on other objects (alibis, evidence dates)
- form `clean_<field>()` methods - rules that only make sense in a form

## Views

All views are class-based. The list views share `FilteredListMixin` (`common/mixins.py`), which applies the filter form and the sorting, so each view only describes its own filters. Create, update and delete views redirect after success and show a message.

## Templates

- `base.html` with a shared navbar and footer
- `404.html` and `500.html` error pages
- Partials in `templates/partials/` for cards, forms, messages, pagination, empty states and delete confirmation
- Custom template tags and filters in `common/templatetags/coldcase_tags.py`:
  - `{% active_if %}` - highlights the current section in the navbar
  - `{% confidence_meter %}` - inclusion tag that draws the evidence confidence bar
  - `|suspicion_level` - turns the suspicion index into low / medium / high
  - `|days_since` - how many days have passed since a date
  - `|initials` - initials of a suspect when there is no photo

## Project structure

```
coldcase/
├── cases/       case files
├── suspects/    suspects and alibis
├── evidence/    evidence for each case
├── common/      home page, base model, validators, form and view mixins, template tags
├── config/      settings and root URLs
├── templates/   all templates, including 404.html and partials/
└── static/      CSS
```
