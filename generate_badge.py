import json
import os
import io
import math
import requests
from PIL import Image, ImageDraw, ImageFont

# ─── 21 Obtainable Levels Table ───
LEVEL_MAP = {
    1:  ("0x1", "NEOPHYTE"),
    2:  ("0x2", "APPRENTICE"),
    3:  ("0x3", "PATHFINDER"),
    4:  ("0x4", "SEEKER"),
    5:  ("0x5", "VISIONARY"),
    6:  ("0x6", "VOYAGER"),
    7:  ("0x7", "ADEPT"),
    8:  ("0x8", "HACKER"),
    9:  ("0x9", "MAGE"),
    10: ("0xA", "WIZARD"),
    11: ("0xB", "MASTER"),
    12: ("0xC", "GURU"),
    13: ("0xD", "LEGEND"),
    14: ("0xE", "GUARDIAN"),
    15: ("0xF", "TITAN"),
    16: ("0x10", "SAGE"),
    17: ("0x11", "VANGUARD"),
    18: ("0x12", "SHOGUN"),
    19: ("0x13", "ASCENDED"),
    20: ("0x14", "MYTHIC"),
    21: ("0x15", "GRANDMASTER")
}

def get_level_tag(level_num):
    if level_num in LEVEL_MAP:
        hex_tag, title = LEVEL_MAP[level_num]
        return f"[{hex_tag}][{title}]"
    return f"[0x{hex(level_num)[2:].upper()}][LEVEL {level_num}]"

# ─── Vector Icon Helpers ───
def draw_trophy(draw, x, y, color=(140, 155, 175)):
    draw.polygon([(x + 2, y + 2), (x + 10, y + 2), (x + 8, y + 9), (x + 4, y + 9)], fill=color)
    draw.line([(x + 6, y + 9), (x + 6, y + 12)], fill=color, width=2)
    draw.line([(x + 3, y + 12), (x + 9, y + 12)], fill=color, width=2)
    draw.arc([(x, y + 2), (x + 5, y + 7)], 90, 270, fill=color, width=1)
    draw.arc([(x + 7, y + 2), (x + 12, y + 7)], 270, 90, fill=color, width=1)

def draw_fire(draw, x, y, color=(140, 215, 45)):
    draw.ellipse([(x + 1, y + 2), (x + 9, y + 11)], fill=color)
    draw.polygon([(x + 2, y + 5), (x + 5, y), (x + 8, y + 5)], fill=color)
    draw.ellipse([(x + 3, y + 5), (x + 7, y + 9)], fill=(13, 17, 23))

def draw_rosette(draw, x, y, color=(185, 60, 235)):
    draw.ellipse([(x + 1, y), (x + 9, y + 8)], fill=color)
    draw.ellipse([(x + 3, y + 2), (x + 7, y + 6)], fill=(13, 17, 23))
    draw.polygon([(x + 3, y + 7), (x + 1, y + 12), (x + 4, y + 10)], fill=color)
    draw.polygon([(x + 7, y + 7), (x + 9, y + 12), (x + 6, y + 10)], fill=color)

def draw_door(draw, x, y, color=(70, 130, 245)):
    draw.rounded_rectangle([(x + 1, y), (x + 9, y + 11)], radius=2, fill=color)
    draw.rectangle([(x, y + 10), (x + 10, y + 12)], fill=color)
    draw.point((x + 3, y + 6), fill=(13, 17, 23))

def draw_thm_logo(draw, x, y):
    draw.arc([(x, y + 2), (x + 14, y + 14)], 160, 360, fill=(255, 255, 255), width=2)
    draw.arc([(x + 10, y - 2), (x + 24, y + 14)], 190, 360, fill=(255, 255, 255), width=2)
    draw.arc([(x + 18, y + 4), (x + 28, y + 14)], 260, 60, fill=(255, 255, 255), width=2)
    draw.line([(x + 2, y + 14), (x + 26, y + 14)], fill=(255, 255, 255), width=2)

    dots = [(2, 17), (5, 17), (8, 17), (3, 20), (6, 20), (2, 23), (7, 23), (9, 23)]
    for dx, dy in dots:
        draw.rectangle([(x + dx, y + dy), (x + dx + 1, y + dy + 1)], fill=(220, 230, 240))

# ─── Avatar Download ───
def download_avatar(avatar_url):
    os.makedirs('docs', exist_ok=True)
    avatar_path = os.path.join('docs', 'avatar.jpg')
    
    if not avatar_url:
        return None

    try:
        res = requests.get(avatar_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if res.status_code == 200:
            with open(avatar_path, 'wb') as f:
                f.write(res.content)
            print(f"✅ Avatar saved to {avatar_path}")
            return Image.open(io.BytesIO(res.content)).convert('RGBA')
    except Exception as e:
        print(f"⚠️ Failed to download avatar: {e}")

    if os.path.exists(avatar_path):
        return Image.open(avatar_path).convert('RGBA')
    return None

# ─── Main Badge Drawing ───
def draw_badge():
    with open('data.json', 'r') as f:
        data = json.load(f)

    profile = data.get('data', {})

    username = profile.get('username', 'User')
    level = profile.get('level', 1)
    level_tag = get_level_tag(level)

    badgesNumber = profile.get('badgesNumber', 0)
    rooms = profile.get('completedRoomsNumber', 0)
    rank = profile.get('rank', 'N/A')
    top_percentage = profile.get('topPercentage')
    streak = profile.get('streak', 0)
    avatar_url = profile.get('avatar', '')

    avatar_img = download_avatar(avatar_url)

    # Width set to 600 to cleanly accommodate top %, rank, and [0xB][MASTER]
    width, height = 600, 110
    radius = 16

    card = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Base card
    draw.rounded_rectangle(
        [(0, 0), (width - 1, height - 1)],
        radius=radius,
        fill=(13, 17, 23, 255),
        outline=(48, 54, 61, 255),
        width=1
    )

    # Wave graphic overlay
    wave_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    wave_draw = ImageDraw.Draw(wave_overlay)
    for i in range(16):
        pts = []
        for x in range(320, width):
            y = int(52 + 18 * math.sin((x + i * 16) / 38.0) + (x - 320) * 0.12)
            pts.append((x, y))
        wave_draw.line(pts, fill=(46, 160, 67, 18), width=1)
    card = Image.alpha_composite(card, wave_overlay)
    draw = ImageDraw.Draw(card)

    # Fonts
    font_bold = font_regular = font_small = font_pill = None
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf"
    ]:
        if os.path.exists(p):
            try:
                font_bold = ImageFont.truetype(p, 17)
                font_regular = ImageFont.truetype(p, 13)
                font_small = ImageFont.truetype(p, 10)
                font_pill = ImageFont.truetype(p, 9)
                break
            except Exception:
                continue

    if not font_bold:
        font_bold = font_regular = font_small = font_pill = ImageFont.load_default()

    # Circular Avatar
    avatar_size = 72
    avatar_x, avatar_y = 18, 19

    if not avatar_img:
        avatar_img = Image.new('RGBA', (avatar_size, avatar_size), (35, 40, 50, 255))

    avatar_img = avatar_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (avatar_size, avatar_size), 0)
    ImageDraw.Draw(mask).ellipse([(0, 0), (avatar_size, avatar_size)], fill=255)
    card.paste(avatar_img, (avatar_x, avatar_y), mask)

    # Green accent ring around avatar
    draw.ellipse(
        [(avatar_x - 3, avatar_y - 3), (avatar_x + avatar_size + 2, avatar_y + avatar_size + 2)],
        outline=(46, 160, 67, 255),
        width=2
    )

    # Header: Username + Lightning Bolt + [0xB][MASTER]
    text_x = 108
    draw.text((text_x, 18), username, fill=(255, 255, 255), font=font_bold)
    name_w = font_bold.getbbox(username)[2] - font_bold.getbbox(username)[0]

    bolt_x = text_x + name_w + 8
    draw.polygon(
        [(bolt_x + 4, 19), (bolt_x, 26), (bolt_x + 3, 26), (bolt_x + 1, 32), (bolt_x + 7, 24), (bolt_x + 4, 24)],
        fill=(245, 158, 11)
    )
    draw.text((bolt_x + 13, 18), level_tag, fill=(190, 200, 215), font=font_bold)

    # Inline Stats Row
    stat_y = 51
    curr_x = text_x

    # 1. Trophy (Rank) + Top % Badge
    draw_trophy(draw, curr_x, stat_y)
    curr_x += 16
    draw.text((curr_x, stat_y - 1), str(rank), fill=(225, 230, 240), font=font_regular)
    curr_x += (font_regular.getbbox(str(rank))[2] - font_regular.getbbox(str(rank))[0])

    # Draw Top % Pill tag if available
    if top_percentage:
        top_str = f"top {top_percentage}%"
        curr_x += 5
        pill_w = (font_pill.getbbox(top_str)[2] - font_pill.getbbox(top_str)[0]) + 8
        pill_h = 13
        pill_y = stat_y - 1
        
        # Subtle dark pill background with golden-orange text
        draw.rounded_rectangle(
            [(curr_x, pill_y), (curr_x + pill_w, pill_y + pill_h)],
            radius=3,
            fill=(33, 40, 52, 255)
        )
        draw.text((curr_x + 4, pill_y + 1), top_str, fill=(245, 180, 50), font=font_pill)
        curr_x += pill_w + 12
    else:
        curr_x += 14

    # 2. Flame (Streak)
    draw_fire(draw, curr_x, stat_y - 1)
    curr_x += 14
    streak_str = f"{streak} days"
    draw.text((curr_x, stat_y - 1), streak_str, fill=(225, 230, 240), font=font_regular)
    curr_x += (font_regular.getbbox(streak_str)[2] - font_regular.getbbox(streak_str)[0]) + 14

    # 3. Rosette (badgesNumber)
    draw_rosette(draw, curr_x, stat_y - 1)
    curr_x += 14
    draw.text((curr_x, stat_y - 1), str(badgesNumber), fill=(225, 230, 240), font=font_regular)
    curr_x += (font_regular.getbbox(str(badgesNumber))[2] - font_regular.getbbox(str(badgesNumber))[0]) + 14

    # 4. Door (Rooms)
    draw_door(draw, curr_x, stat_y - 1)
    curr_x += 14
    draw.text((curr_x, stat_y - 1), str(rooms), fill=(225, 230, 240), font=font_regular)

    # Domain text
    draw.text((text_x, 76), "tryhackme.com", fill=(160, 170, 185), font=font_regular)

    # Top-right TryHackMe Logo
    logo_x = width - 85
    draw_thm_logo(draw, logo_x, 15)
    thm_txt_x = logo_x + 32
    draw.text((thm_txt_x, 12), "Try", fill=(255, 255, 255), font=font_small)
    draw.text((thm_txt_x, 22), "Hack", fill=(255, 255, 255), font=font_small)
    draw.text((thm_txt_x, 32), "Me", fill=(255, 255, 255), font=font_small)

    card.save('docs/tryhackme_badge.png', 'PNG')
    print(f'✅ Badge generated with top {top_percentage}% and saved to docs/tryhackme_badge.png')

if __name__ == '__main__':
    draw_badge()
