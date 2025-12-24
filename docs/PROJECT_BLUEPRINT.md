# Project Blueprint (Reusable Template)

Use this blueprint for every new repo/project. Keep it minimal, repeatable, and fast.

---

## 1) Standard Repo Structure

```
<project>/
├── core/                # reusable Python modules
│   └── ...              # pipelines, utils, business logic
├── data/
│   ├── raw/             # never committed
│   └── processed/       # optional to commit
├── notebooks/           # Jupyter only
├── docs/                # project docs
├── tests/               # optional
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 2) Non-Negotiable Rules

- `data/raw/` is **local only** and **never committed**
- `.env` files are **never committed**
- Git work happens in **small blocks**:
  1) change one thing
  2) commit
  3) push
- No overwriting/deleting files unless explicitly allowed

---

## 3) Minimal .gitignore

```gitignore
__pycache__/
*.py[cod]
.ipynb_checkpoints/

.venv/
env/
venv/

data/raw/*
!data/raw/.gitkeep

.DS_Store
.vscode/
.idea/

.env
*.env
```

---

## 4) Local Python Environment

Create venv in repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Register kernel (optional but recommended):

```bash
pip install ipykernel
python -m ipykernel install --user --name "<project>" --display-name "Python (<project>)"
```

---

## 5) How to Start Jupyter (Always)

Start Jupyter from **repo root**:

```bash
cd <project>
source .venv/bin/activate
jupyter lab
```

Paths in notebooks should assume repo root as CWD:

```python
from pathlib import Path
PROJECT_ROOT = Path.cwd()
```

---

## 6) “Block” Commit Protocol

For each block:

```bash
git add <files>
git commit -m "Describe the block"
git push
```

---

## 7) First Commit Checklist

- `.gitignore` exists and ignores `data/raw/*`
- `data/raw/.gitkeep` exists
- `README.md` exists
- `requirements.txt` exists
- `docs/PROJECT_BLUEPRINT.md` exists
