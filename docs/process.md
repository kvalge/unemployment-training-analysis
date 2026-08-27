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

8. **Monthly sent vs participated**
   - Added `src/analysis/monthly_training.py`: by start month, count all IDs sent to training vs IDs who participated (`lõpetas` or `katkestas`). Wrote `output/txt/monthly_training.txt` and `output/png/analysis/monthly_sent_vs_participated.png`.

9. **Chart colours**
   - Set PNG colours to main `#4ba7a2` and secondary `#9cd8da`, then regenerated EDA and analysis figures.

10. **Share sent vs not sent among unemployed**
    - Added `src/analysis/sent_share.py`: share of unemployed sent to training vs not sent, by county, age group, and gender. Wrote `output/txt/sent_share.txt` and three figures in `output/png/analysis`.

11. **Completion vs dropout among participants**
    - Added `src/analysis/completion_share.py`: counts and shares of `lõpetas` vs `katkestas` among participants, by county, age group, gender, subject, and calendar month. Wrote `output/txt/completion_share.txt` and five figures in `output/png/analysis`.

12. **Project README**
    - Wrote `README.md` with links to `ANALYSIS.md`, `docs/process.md`, and the `output/txt` and `output/png` folders, plus setup and how to run the scripts.

13. **Pipeline entry point**
    - Added `main.py` to run download/ensure raw data, load, EDA, and all analysis scripts in order. Added `src/load_data/download.py`.
