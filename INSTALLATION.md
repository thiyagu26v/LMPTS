# Installation Guide

## System Requirements

- **OS:** Windows 10+, macOS 10.14+, or Linux
- **Python:** 3.10 or higher
- **RAM:** 512 MB minimum
- **Disk:** 50 MB

## Step 1: Clone or Download

Place the project in your workspace:
```
sugunew/
```

## Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
cd sugunew
pip install -r requirements.txt
```

## Step 4: Verify Installation

```bash
python -m pytest tests/ -v --tb=short
```

Expected: 95 tests passed.

## Step 5: Run Application

```bash
python main.py
```

The GUI window opens with four tabs: Admin Panel, Learner Portal, Learning Paths, Analytics Dashboard.

## Database Location

Default: `sugunew/data/lmpts.db`

Created automatically on first run with seed data.

## Development Tools (Optional)

```bash
pip install black isort flake8 mypy
black lmpts tests
isort lmpts tests
flake8 lmpts tests
mypy lmpts
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: lmpts` | Run from `sugunew/` directory |
| Tkinter not found | Install `python3-tk` (Linux) |
| Database locked | Close other instances |
| Tests fail on seed data | Delete `data/lmpts.db` and retry |
