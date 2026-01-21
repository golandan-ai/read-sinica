# Read Sinica - Liaoshi Navigator

Navigate to any chapter of the History of Liao (遼史) in Academia Sinica's database.

## Structure

```
read-sinica/
├── read_sinica_liaoshi.html   # Web interface
├── read/
│   ├── navigate_sinica.py     # Python automation script
│   └── requirements.txt
├── vercel.json
└── commit.md                  # Project summary for Claude
```

## Web Interface

Hosted on Vercel. Enter a chapter number (1-116) to:
- See the Chinese chapter name
- Open Sinica database
- Copy Python command for local automation

## Python Script (Local)

### Setup
```bash
cd read
pip install -r requirements.txt
playwright install chromium
```

### Usage
```bash
python navigate_sinica.py 1      # Opens 卷一 本紀第一
python navigate_sinica.py 35     # Opens 卷三十五 志第五
python navigate_sinica.py 75     # Opens 卷七十五 列傳第五
```

## Chapter Ranges

| Range   | Section     | Chinese |
|---------|-------------|---------|
| 1-30    | Annals      | 本紀    |
| 31-60   | Treatises   | 志      |
| 61-70   | Tables      | 表      |
| 71-116  | Biographies | 列傳    |
