# Process log

Completed tasks, newest last.

## 2026-08-27

1. **Load raw data**
   - Added `src/load_data` to read both Excel files from `data/raw`: `töötud.xls` (unemployed persons) and `koolitused.xls` (trainings).
   - Loader strips string columns, parses dates, and exposes `load_unemployed`, `load_trainings`, and `load_raw_data`.
   - Recorded `pandas` and `xlrd` in `requirements.txt`.

2. **Start a process log**
   - Record completed work in `docs/process.md` after every finished task.
   - Added a project rule so this is done automatically from now on.

3. **Commit messages in chat**
   - After every completed task, write a copy-pasteable commit message in the chat reply.
   - Added a project rule for this. Do not create a git commit unless asked.

4. **Exploratory data analysis (univariate)**
   - Added `src/inspect/eda.py` to profile both tables separately: overview, descriptives, histograms, and boxplots.
   - Wrote `output/txt` and `output/png`, and recorded findings in `ANALYSIS.md` in analysis order.

5. **Value labels on figures**
   - Added counts, percentages, and five-number summaries onto the EDA PNGs so the numbers are readable on the charts.

6. **Separate EDA figure folder**
   - Moved exploratory PNGs to `output/png/eda` so later figures can live in other folders under `output/png`.

7. **Inclusive training duration**
   - Training length is now end minus start plus one day, so a same-day course counts as 1 day. Regenerated descriptives, overview, duration plots, and `ANALYSIS.md`.
