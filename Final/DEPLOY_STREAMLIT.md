# Public salary dashboard

## Streamlit Community Cloud settings

- Repository: `85913286lcr/group5-project1-assignment`
- Branch: `Rachelle-LIU`
- Main file path: `Final/cloud_app.py`
- Advanced settings: Python `3.11`
- Dependencies: `Final/requirements.txt`
- Data: `Final/jobs_clean.csv`, loaded relative to the dashboard source file.

Sign in at https://share.streamlit.io/, create an app from this repository,
and enter the settings above. Choose an available app subdomain and deploy.
Verify the app's sharing settings allow public access. Test the final URL in
an incognito window before sharing it with the team.

## Expected default view

- 140,866 IT postings
- 134,503 analysis-ready postings
- 6,363 excluded for review
- Median advertised monthly salary midpoint: SGD 6,500.00
- Nine position levels

Both filters affect the overview, bar chart, salary distribution and summary.
The source data describes historical job advertisements, not current employee pay.

## Local run

From the repository root:

```sh
python -m pip install -r Final/requirements.txt
python -m streamlit run Final/cloud_app.py
```

Dependencies match the existing local salary_dashboard environment. Use Python
3.11 with these pinned versions. The published URL is only available after a
successful deployment; localhost:8501 is not a public URL.
