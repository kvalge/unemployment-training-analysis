# Unemployment Training Analysis

Quick links:

- [Analysis write-up](ANALYSIS.md)
- [Process log](docs/process.md)
- Text outputs: [output/txt](output/txt)
- Figures: [output/png/eda](output/png/eda) (exploratory) · [output/png/analysis](output/png/analysis) (analysis)

---

Analysis of Estonian unemployment register extracts: people registered as unemployed (`töötud.xls`) and labour-market trainings (`koolitused.xls`). The two tables share `ID`.

## Data

| File | Table | Contents |
| --- | --- | --- |
| `data/raw/töötud.xls` | Unemployed persons | ID, sex, age, county, unemployment start/end |
| `data/raw/koolitused.xls` | Trainings | ID, training start/end, occupation, result, training card |

Place the raw Excel files in `data/raw` if they are not already there.

## Setup

```text
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

From the project root (so `src` imports resolve):

```text
python main.py
```

That runs the full pipeline: ensure/download raw Excel files, load both tables, exploratory analysis, then all analysis scripts. Outputs go to `output/txt` and `output/png`.

To run a single step:

```text
python -c "from src.load_data import load_raw_data; u, t = load_raw_data(); print(u.shape, t.shape)"
python -c "from src.inspect.eda import run_eda; run_eda()"
python -c "from src.analysis.monthly_training import run_monthly_training_analysis; run_monthly_training_analysis()"
python -c "from src.analysis.sent_share import run_sent_share_analysis; run_sent_share_analysis()"
python -c "from src.analysis.completion_share import run_completion_share_analysis; run_completion_share_analysis()"
```

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
```

Chart colours: main `#4ba7a2`, secondary `#9cd8da`. Training duration is inclusive (`end − start + 1` days).
