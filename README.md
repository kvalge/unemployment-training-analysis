# Unemployment Training Analysis

Quick links:

- [Analysis write-up](ANALYSIS.md)
- [Process log](docs/process.md)
- [Task prompts](docs/commands.md)
- Text outputs: [output/txt](output/txt)
- Figures: [output/png/eda](output/png/eda) (exploratory) · [output/png/analysis](output/png/analysis) (analysis)

---

## Data

| File | Table | Contents |
| --- | --- | --- |
| `data/raw/töötud.xls` | Unemployed persons | ID, sex, age, county, unemployment start/end |
| `data/raw/koolitused.xls` | Trainings | ID, training start/end, occupation, result, training card |
Every ID of `koolitused.xls` referes to unemployed person of `töötud.xls`.

## Setup

```text
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

```text
python main.py
```

That runs the full pipeline: ensure/download raw Excel files, load both tables, exploratory analysis, then all analysis scripts. Outputs go to `output/txt` and `output/png`.

## Project layout

```text
data/raw/               raw Excel extracts
src/load_data/          download/ensure and load both tables
src/inspect/            EDA
src/analysis/           monthly starts, sent vs not sent, completion vs dropout
main.py                 run the full pipeline
output/txt/             numeric tables
output/png/eda/         exploratory charts
output/png/analysis/    analysis charts
ANALYSIS.md             findings in analysis order
docs/process.md         log of completed tasks
docs/commands.md        prompt text for each completed task
```

Chart colours: main `#4ba7a2`, secondary `#9cd8da`. Training duration is inclusive (`end − start + 1` days).
