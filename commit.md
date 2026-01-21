# Read Sinica - Liaoshi Navigator

## Project Summary

A tool to quickly navigate to specific chapters of the History of Liao (遼史) in Academia Sinica's Chinese text database.

## Components

### 1. Web Interface (`read_sinica_liaoshi.html`)
- Input box for chapter number (1-116)
- Displays Chinese chapter name (e.g., 遼史卷一 本紀第一)
- "Open Sinica" button opens the database
- "Copy Command" button copies Python command

### 2. Python Script (`read/navigate_sinica.py`)
- Uses Playwright to automate browser navigation
- Navigates: 史 → 正史 → 遼史 → [Section] → Chapter
- Must run locally (cannot run on web server)

## Chapter Ranges
| Range   | Section     | Chinese |
|---------|-------------|---------|
| 1-30    | Annals      | 本紀    |
| 31-60   | Treatises   | 志      |
| 61-70   | Tables      | 表      |
| 71-116  | Biographies | 列傳    |

## Deployment

### GitHub Repository Structure
```
read-sinica/
├── read_sinica_liaoshi.html   ← webpage
├── read/
│   ├── navigate_sinica.py     ← Python script
│   └── requirements.txt
├── vercel.json
├── README.md
└── commit.md
```

### Vercel Deployment
- Import GitHub repo to Vercel
- Vercel serves `read_sinica_liaoshi.html` as the main page
- URL: https://[project-name].vercel.app

## Local Usage

```bash
cd read
pip install -r requirements.txt
playwright install chromium
python navigate_sinica.py <chapter_number>
```

## Key Technical Details

- Uses Sinica free access URL: `https://hanchi.ihp.sinica.edu.tw/ihpc/ttswebquery?@hanjiquery`
- Tree navigation clicks + icons (m+.gif, mm+.gif) to expand
- TreeWalker finds exact text matches, walks up parent hierarchy to find + icons
- 3-second waits between clicks allow Sinica server to respond

## Future Improvements
- Add section dropdown (本紀/志/表/列傳) to webpage
- Save last used chapter in localStorage
- Add direct links to downloaded chapters
