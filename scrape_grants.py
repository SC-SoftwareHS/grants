import requests, io, pandas as pd, pdfplumber, datetime as dt
BASE = "https://www.schoolsafety.gov/print/view/pdf/grants_finder_view/default"
params = {"application_month":"all","application_year":"all"}        # add filters here

pdf_bytes = requests.get(BASE, params=params, timeout=60).content
with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
    text = "\n".join(page.extract_text() for page in pdf.pages)

records = []
block = {}
for line in text.splitlines():
    if line.startswith("Department"):
        block["agency"] = line.strip()
    elif line.startswith("Deadline:"):
        block["deadline"] = line.replace("Deadline:", "").strip()
    elif line.startswith("Description:"):
        block["description"] = line.replace("Description:", "").strip()
    elif line.startswith("Access Link:"):
        block["link"] = line.replace("Access Link:", "").strip()
        records.append(block); block = {}
    else:
        # first non‑department line is always the grant title
        if "title" not in block and line.strip():
            block["title"] = line.strip()

df = pd.DataFrame(records)
df["pulled_on"] = dt.date.today()
df.to_csv("grants.csv", index=False)
