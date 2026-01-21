"""
Sinica Navigator - Opens Liaoshi at a specific chapter
======================================================

Usage: python navigate_sinica.py <chapter_number>

Navigation: 史 → 正史 → 遼史 → [Section] → Chapter
"""

import sys
import io
import asyncio
import argparse

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: playwright not installed.")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Free access URL
SINICA_FREE_URL = "https://hanchi.ihp.sinica.edu.tw/ihpc/ttswebquery?@hanjiquery"

# Chinese numerals
CHINESE_NUMS = {
    1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九', 10: '十',
    11: '十一', 12: '十二', 13: '十三', 14: '十四', 15: '十五', 16: '十六', 17: '十七', 18: '十八', 19: '十九', 20: '二十',
    21: '二十一', 22: '二十二', 23: '二十三', 24: '二十四', 25: '二十五', 26: '二十六', 27: '二十七', 28: '二十八', 29: '二十九', 30: '三十',
    31: '三十一', 32: '三十二', 33: '三十三', 34: '三十四', 35: '三十五', 36: '三十六', 37: '三十七', 38: '三十八', 39: '三十九', 40: '四十',
    41: '四十一', 42: '四十二', 43: '四十三', 44: '四十四', 45: '四十五', 46: '四十六', 47: '四十七', 48: '四十八', 49: '四十九', 50: '五十',
    51: '五十一', 52: '五十二', 53: '五十三', 54: '五十四', 55: '五十五', 56: '五十六', 57: '五十七', 58: '五十八', 59: '五十九', 60: '六十',
    61: '六十一', 62: '六十二', 63: '六十三', 64: '六十四', 65: '六十五', 66: '六十六', 67: '六十七', 68: '六十八', 69: '六十九', 70: '七十',
    71: '七十一', 72: '七十二', 73: '七十三', 74: '七十四', 75: '七十五', 76: '七十六', 77: '七十七', 78: '七十八', 79: '七十九', 80: '八十',
    81: '八十一', 82: '八十二', 83: '八十三', 84: '八十四', 85: '八十五', 86: '八十六', 87: '八十七', 88: '八十八', 89: '八十九', 90: '九十',
    91: '九十一', 92: '九十二', 93: '九十三', 94: '九十四', 95: '九十五', 96: '九十六', 97: '九十七', 98: '九十八', 99: '九十九', 100: '一百',
    101: '一百一', 102: '一百二', 103: '一百三', 104: '一百四', 105: '一百五', 106: '一百六', 107: '一百七', 108: '一百八', 109: '一百九', 110: '一百十',
    111: '一百十一', 112: '一百十二', 113: '一百十三', 114: '一百十四', 115: '一百十五', 116: '一百十六',
}


def get_section_info(chapter_num: int) -> tuple:
    """Returns (section_name, section_number) for a chapter"""
    if 1 <= chapter_num <= 30:
        return ('本紀', chapter_num)
    elif 31 <= chapter_num <= 60:
        return ('志', chapter_num - 30)
    elif 61 <= chapter_num <= 70:
        return ('表', chapter_num - 60)
    elif 71 <= chapter_num <= 116:
        return ('列傳', chapter_num - 70)
    return (None, None)


async def click_tree_item(page, search_text: str):
    """
    Click the + icon next to a tree item to expand it.
    This is the EXACT same method used in the working liaoshi_scraper.
    """
    result = await page.evaluate('''(searchText) => {
        // Get all elements and find the one with our text
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim() === searchText) {
                // Found the text node - now find the + icon nearby
                let parent = node.parentElement;

                // Walk up and look for siblings/cousins that are + icons
                for (let i = 0; i < 5 && parent; i++) {
                    // Look for img elements that could be + icons
                    const imgs = parent.querySelectorAll('img');
                    for (let img of imgs) {
                        const src = (img.src || '').toLowerCase();
                        // Sinica uses m+.gif, mm+.gif for expand icons
                        if (src.includes('m+.gif') || src.includes('mm+.gif') ||
                            src.includes('cl.gif') || src.includes('+')) {
                            img.click();
                            return 'plus-img:' + searchText + ' src:' + src.split('/').pop();
                        }
                    }

                    parent = parent.parentElement;
                }

                // If no + found, try clicking the text element itself
                node.parentElement.click();
                return 'text-click:' + searchText;
            }
        }

        return null;
    }''', search_text)

    return result


async def click_tree_item_partial(page, search_text: str):
    """
    Click the + icon next to a tree item containing the search text (partial match).
    """
    result = await page.evaluate('''(searchText) => {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.includes(searchText)) {
                let parent = node.parentElement;

                for (let i = 0; i < 5 && parent; i++) {
                    const imgs = parent.querySelectorAll('img');
                    for (let img of imgs) {
                        const src = (img.src || '').toLowerCase();
                        if (src.includes('m+.gif') || src.includes('mm+.gif') ||
                            src.includes('cl.gif') || src.includes('+')) {
                            img.click();
                            return 'plus-img:' + node.textContent.trim().substring(0, 30);
                        }
                    }
                    parent = parent.parentElement;
                }

                node.parentElement.click();
                return 'text-click:' + node.textContent.trim().substring(0, 30);
            }
        }

        return null;
    }''', search_text)

    return result


async def navigate_to_chapter(chapter_num: int):
    """Navigate to a specific Liaoshi chapter"""

    if chapter_num < 1 or chapter_num > 116:
        print(f"ERROR: Chapter must be between 1 and 116")
        return

    chapter_cn = CHINESE_NUMS.get(chapter_num, str(chapter_num))
    section_name, section_num = get_section_info(chapter_num)
    section_cn = CHINESE_NUMS.get(section_num, str(section_num))

    print("=" * 60)
    print(f"SINICA NAVIGATOR - Liaoshi Chapter {chapter_num}")
    print(f"Target: 遼史卷{chapter_cn} {section_name}第{section_cn}")
    print("=" * 60)

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    try:
        # Step 1: Open Sinica
        print(f"\n[1] Opening Sinica database...")
        await page.goto(SINICA_FREE_URL, timeout=60000, wait_until="networkidle")
        print("    Waiting for page to load...")
        await asyncio.sleep(5)

        # Step 2: Find the tree frame
        print(f"\n[2] Finding tree frame...")
        frames = page.frames
        print(f"    Found {len(frames)} frames")

        tree_frame = None
        for frame in frames:
            try:
                frame_content = await frame.evaluate('() => document.body?.innerText?.substring(0, 200) || ""')
                if '史' in frame_content and ('經' in frame_content or '子' in frame_content):
                    tree_frame = frame
                    print(f"    Found tree frame with categories")
                    break
            except:
                pass

        if tree_frame:
            nav_page = tree_frame
            print("    Switched to tree frame")
        else:
            nav_page = page
            print("    Using main page")

        # Debug: Show images on page
        all_imgs = await nav_page.evaluate('''() => {
            const imgs = [];
            document.querySelectorAll('img').forEach(img => {
                const src = img.src || '';
                imgs.push(src.split('/').pop());
            });
            return imgs;
        }''')
        print(f"    Images on page: {all_imgs[:15]}")

        # Step 3: Click 史 (History)
        print(f"\n[3] Expanding 史 (History)...")
        result = await click_tree_item(nav_page, "史")
        print(f"    {result}")
        await asyncio.sleep(3)

        # Step 4: Click 正史 (Official Histories)
        print(f"\n[4] Expanding 正史 (Official Histories)...")
        result = await click_tree_item(nav_page, "正史")
        print(f"    {result}")
        await asyncio.sleep(3)

        # Step 5: Click 遼史 (History of Liao)
        print(f"\n[5] Expanding 遼史 (History of Liao)...")
        result = await click_tree_item(nav_page, "遼史")
        print(f"    {result}")
        await asyncio.sleep(3)

        # Step 6: Click section (本紀, 志, 表, or 列傳)
        print(f"\n[6] Expanding {section_name}...")
        # Use partial match for section (e.g., "本紀　凡三十卷")
        result = await click_tree_item_partial(nav_page, section_name)
        print(f"    {result}")
        await asyncio.sleep(3)

        # Step 7: Click the specific chapter
        print(f"\n[7] Clicking 卷{chapter_cn} {section_name}第{section_cn}...")

        result = await nav_page.evaluate('''(args) => {
            const chapterCn = args.chapterCn;
            const sectionName = args.sectionName;
            const chineseDigits = '一二三四五六七八九十百';

            function isExactMatch(text) {
                const target = '卷' + chapterCn;
                const idx = text.indexOf(target);
                if (idx === -1) return false;
                const afterIdx = idx + target.length;
                if (afterIdx >= text.length) return true;
                return !chineseDigits.includes(text[afterIdx]);
            }

            const links = document.querySelectorAll('a');
            for (let link of links) {
                const text = link.textContent?.trim() || '';
                if (isExactMatch(text) && text.includes(sectionName)) {
                    link.click();
                    return {clicked: true, text: text};
                }
            }

            for (let link of links) {
                const text = link.textContent?.trim() || '';
                if (isExactMatch(text)) {
                    link.click();
                    return {clicked: true, text: text, method: 'fallback'};
                }
            }

            return {clicked: false};
        }''', {'chapterCn': chapter_cn, 'sectionName': section_name})

        print(f"    Result: {result}")

        if result.get('clicked'):
            print(f"\n[SUCCESS] Navigated to 遼史卷{chapter_cn}")
        else:
            print(f"\n[!] Could not auto-click chapter - please click manually")

        print("\n" + "=" * 60)
        print("Browser is ready. Press Ctrl+C to close.")
        print("=" * 60)

        while True:
            await asyncio.sleep(60)

    except KeyboardInterrupt:
        print("\n[*] Closing browser...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        print("\n[*] Keeping browser open. Press Ctrl+C to close.")
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            pass
    finally:
        await browser.close()
        await playwright.stop()


def main():
    parser = argparse.ArgumentParser(description='Navigate to Liaoshi chapter')
    parser.add_argument('chapter', type=int, help='Chapter number (1-116)')
    args = parser.parse_args()
    asyncio.run(navigate_to_chapter(args.chapter))


if __name__ == "__main__":
    main()
