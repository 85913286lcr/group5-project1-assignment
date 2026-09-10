## 🚀Project Hub
This section provides quick access to the key resources and team contributions for our project.
| Resource | Link |
|---|---|
| Assignment Requirements | [View Assignment Requirements](https://github.com/su-ntu-ctp/6m-data-C1.2-coaching-assignment-project/tree/main) |
| Team Objectives | [View Team Objectives](https://docs.google.com/spreadsheets/d/1tD3jOETwZrKOupCvxrJI2OyNYeF9oYJL_96vqHNs4Mc/edit?gid=0#gid=0) |
| Team Google Sheet | [Open Team Google Sheet](https://docs.google.com/spreadsheets/d/1rPKQVOA4BnmLmhWlMDaH5KFtPxwo0GTiYh7P6FZA8bQ/edit?gid=793927632#gid=793927632) |
| Shared Project Folder | [Open Shared Project Folder](https://drive.google.com/drive/folders/1boeRU8icSzqgdaYJlfCVLr7D8G5QFf9_) |
| Adelene – Claude Share | [View Claude Conversation](https://claude.ai/share/352d8c56-28bd-4e51-bbb2-233442379a21) |
| Siew Yin – HR Analysis | [View HR Analysis](https://docs.google.com/document/d/13XBYjDMUy79K1aJ6n4Bd23iJr642wCHjyiXfwaR85i4/edit?usp=sharing) |

## 🚀Getting Started (do this first)
Step 0 — Load a sample, not the whole file. The full file has ~1M rows; taste a spoonful before cooking the whole pot. Build everything on the fast subset, and scale up once it works:

import pandas as pd
df = pd.read_csv('sg_jobs.csv', nrows=50000)   # first 50,000 rows only
Then take your first three EDA steps (adjust column names to what's actually in the file):

df.shape                    # 1. How big is your sample? (rows, columns)
df.info()                   # 2. What columns do you have, and what types are they?
df['salary'].describe()     # 3. Pick one numeric column — what's typical, what's extreme?
That's it — you've started. Everything else in this brief builds on these first looks.

## 🚀Suggested flow:
1. Business case & objective (2–3 mins)
Scenario, users, objective, success criteria.
2. Process & data handling (3–4 mins)
How you cleaned, transformed, and explored the data.
3. Dashboard / app walkthrough (3–4 mins)
Main views, interactions, and how they answer the business question.
4. Challenges & learnings (1–2 mins)
Technical/analytical challenges, what you learned, and possible next steps.

## 🚀Deliverables
1. Brief written report (Markdown/PDF) following Sections 1–4 above.
2. Working dashboard / app (deployed link or clear run instructions).
3. Code repo with:
  Data handling notebook(s) / scripts,
  Dashboard/app code,
  README with setup steps.
4. Focus on a coherent story from business question → data process → dashboard → insights, rather than advanced techniques.



   
