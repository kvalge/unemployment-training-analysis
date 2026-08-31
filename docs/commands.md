# Task prompts

Prompts that produced each completed task in [process.md](process.md). Copy one block to re-run that step (or a similar one) in a new chat.

---

## 1. Load raw data

```text
Write code file to src\load_data to load data from data\raw from both files.
```

---

## 2. Start a process log

```text
Write to docs\process.md what was the task completed. And from now on, write to docs\process.md one by one what was the task done after every task completed.
```

---

## 3. Commit messages in chat

```text
Write commit message to this chat. And from now on, after every completed task write also commit message to chat.
```

---

## 4. Exploratory data analysis (univariate)

```text
Based on data generated from src/load_data/load.py, write the code to conduct exploratory data analysis of both tables separately and for all variables where applicable and meaningful. Write the code to src\inspect. Write the output to the output folder. In the output folder create separate folders for png and txt files. From data find: shape, types, missing values, duplications — to one file. Then sum, avg, count, mean, median, std, iqr — to another file. Create histograms and boxplots. From now on write the analysis results to ANALYSIS.md in logical order as analysis is conducted. Write what was done and conclusions based on analysis, links to output txt files and png files. Display some very general or relevant png pictures visibly inside ANALYSIS.md. All content of ANALYSIS.md should be in logical order, as good analysis should be conducted step by step.
```

---

## 5. Value labels on figures

```text
Add value labels to png-s to see the numbers.
```

---

## 6. Separate EDA figure folder

```text
Move exploratory png-s created so far to a separate folder inside output\png, to keep them separate from png-s that will be created later.
```

---

## 7. Inclusive training duration

```text
Check calculations that calculate avg training duration. When training start and end date is the same, then the training duration is 1 day not zero. Meaning every training duration end minus start date should get +1.
```

---

## 8. Monthly sent vs participated

```text
Create to src\analysis a script to calculate: separated by start date of beginning of training (Koolituse algus) by month, for every month count all who were sent to training (count all ID) and count those who participated (count of ID of koolituse tulemus katkestas and lõpetas only). Create also visualization to output\png\analysis.
```

---

## 9. Chart colours

```text
Change colors of png-s: main #4ba7a2, secondary #9cd8da.
```

---

## 10. Share sent vs not sent among unemployed

```text
Create to src\analysis a script to calculate: share of all count ID of koolitused and share of count ID from töötud which ID is not in koolitused from all count ID of töötud (share of sent to training and share of not sent to training from all unemployed). And this separately by: county, age groups, gender. Generate visuals to output\png\analysis.
```

---

## 11. Completion vs dropout among participants

```text
Create to src\analysis a script to calculate: count of ID of koolituse tulemus katkestas and lõpetas, count of katkestas, count of lõpetas, share of both from katkestas+lõpetas. And this separately by: county, age group, gender, subject (koolituse ametiala), month (not by year and month, but month). Create visuals.
```

---

## 12. Project README

```text
Write usual relevant info to README.md. To the top of the file add also links to ANALYSIS.md and docs/process.md and links from where to find outputs of txt and png files.
```

---

## 13. Pipeline entry point

```text
Create to project root main.py that runs all process from downloading to analysis.
```

---

## 14. Task prompt catalog

```text
Based on docs/process.md, create docs\commands.md content, task by task, what should be the prompt text of the task to get the task done. Add a link to this also to README.md.
```

---

## 15. Patterns and interactions

```text
After completing the preliminary overview and basic exploratory analysis, identify meaningful patterns, relationships, trends, and differences in the data that could provide actionable insights. Focus on exploring interactions between variables, unusual patterns or outliers, and factors that may explain important outcomes or differences between groups or changes over time. Write a separate code file for that if needed and output files. Write a summary to the end of ANALYSIS.md.
```

---

## 16. Unemployment length vs training

```text
Write separate analyses code file, outputs files and add it to ANALYSIS.md - under 13.: compare persons not sent to training and those who participated on training (lõpetas ja katkestas) based on unemployment period length; under 14.: compare lõpetas ja katkestas based on unemployment period length; In both cases use Töötuse algus ja töötuse lõpp and also Koolituse algus ja töötuse lõpp. The goal is to analyse if the training has impact on unemployment period length and end.
```

---

## 18. Three-way training status

```text
Create a separate script file to compute the distribution of unemployed individuals across three training status categories: not sent to training, not participated (jäi ära, keeldus, loobus), and participants (osales, katkestas). For each category, calculate the count and percentage of all unemployed people, and also break this down by subcategories such as county, sex, age group, koolituse ametiala, koolituskaart, so that for every subcategory combination we can see how the three status categories are distributed. Present the results as summary tables, one for the overall distribution and one for each breakdown dimension, so the output can later be used to build faceted comparison charts across categories. Generate separate output files. Add result to ANALYSIS.md under 15, summary moves to be 16. Update then also Summary of actionable insights.
```

---

## 19. Faceted training-status charts

```text
Create a faceted bar chart that shows, for each county, the percentage breakdown of unemployed people across the three training status categories (not sent to training, not participated, participants), so that county panels can be compared side by side. Each panel should represent one county, with bars inside the panel representing the three status categories, using consistent colors for the same category across all panels so patterns can be spotted by eye. Use the same y-axis scale across all panels so percentages are directly comparable between counties, and sort the panels by one of the categories, for example by the percentage of not participated, so that counties with the highest values appear first. Add a horizontal reference line in each panel showing the overall average percentage for that category across all counties, so it is easy to see which counties deviate from the average. Repeat the same faceted structure for sex and age group as additional breakdown dimensions, producing separate figures or an additional facet layer, so the same three status categories can be compared not only across counties but also across demographic subgroups within counties. Update also ANALYSIS.md, write that result under 16 and update Summary of actionable insights, which will be 17.
```

---

## 21. Facet charts sorted by not sent; age × sex

```text
ANALYSIS.md 16. Faceted comparison of the three training statuses - sort png graphs by 'not sent'. Create code file and output png for training status by age group and sex
```
