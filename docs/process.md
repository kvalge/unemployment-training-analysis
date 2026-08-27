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
