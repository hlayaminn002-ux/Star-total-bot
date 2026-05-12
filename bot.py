import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)

TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o"


# =========================
# TEXT NORMALIZE
# =========================

def normalize_text(text):
    text = text.lower().strip()

    replacements = {
        "၊": " ",
        ",": " ",
        "/": " ",
        "  ": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


# =========================
# EXTRACT AMOUNT
# =========================

def extract_amount(line, default_amount):

    # 12r500
    r_style = re.search(r'(\d+)r(\d+)', line)
    if r_style:
        return int(r_style.group(2))

    # last number
    amount_match = re.search(r'(\d+)\s*$', line)

    if amount_match:
        return int(amount_match.group(1))

    return default_amount


# =========================
# EXTRACT DIGITS
# =========================

def extract_digits(text):
    return re.findall(r'\d', text)


def extract_pairs(text):
    return re.findall(r'\d{2}', text)


# =========================
# MAIN LOGIC
# =========================

def calculate_line_logic(line, default_amount):

    original = line
    line = normalize_text(line)

    if not line:
        return 0

    if "%" in line:
        return 0

    amount = extract_amount(line, default_amount)

    if amount <= 0:
        return 0

    # remove ending amount
    clean_line = re.sub(r'\d+\s*$', '', line).strip()

    digits = extract_digits(clean_line)
    pairs = extract_pairs(clean_line)

    total = 0

    # =========================
    # R CHECK
    # =========================

    is_r = bool(re.search(r'(^|\s)r($|\s)', clean_line))
    if "အာ" in clean_line:
        is_r = True

    # =========================
    # PRIORITY RULES
    # =========================

    # --------------------------------
    # ပတ်ပူး / ထိပ်နောက်
    # --------------------------------

    if any(k in clean_line for k in [
        "ပတ်ပူး",
        "ပူးပို",
        "ထိပ်နောက်",
        "ထန"
    ]):

        return len(digits) * 20 * amount

    # --------------------------------
    # ပတ် / အပါ
    # --------------------------------

    if any(k in clean_line for k in [
        "အပါ",
        "ပတ်",
        "ပါ9ပတ်"
    ]):

        return len(digits) * 19 * amount

    # --------------------------------
    # ခွေ / ခွေပူး
    # --------------------------------

    if "ခွေ" in clean_line:

        num_match = re.search(r'(\d+)', clean_line)

        if num_match:

            count = len(num_match.group(1))

            if "ပူး" in clean_line:
                return (count * count) * amount

            return (count * (count - 1)) * amount

    # --------------------------------
    # ကပ် / ကို
    # --------------------------------

    if any(k in clean_line for k in ["ကပ်", "ကို"]):

        nums = re.findall(r'(\d+)', clean_line)

        if len(nums) >= 2:

            base = len(nums[0]) * len(nums[1])

            if is_r:
                base *= 2

            return base * amount

    # --------------------------------
    # ထိပ် / ပိတ် / ဘရိတ်
    # --------------------------------

    if any(k in clean_line for k in [
        "ထိပ်",
        "top",
        "t"
    ]):

        return max(len(digits), 1) * 10 * amount

    if any(k in clean_line for k in [
        "ပိတ်",
        "နောက်",
        "န",
        "bk",
        "ဘရိတ်"
    ]):

        return max(len(digits), 1) * 10 * amount

    # --------------------------------
    # SPECIAL
    # --------------------------------

    temp = 0

    if any(k in clean_line for k in [
        "ပါဝါ",
        "pw",
        "power"
    ]):
        temp += 10

    if any(k in clean_line for k in [
        "ညီကို",
        "ညီအကို",
        "ညီအစ်ကို"
    ]):
        temp += 20

    if any(k in clean_line for k in [
        "နက္ခတ်",
        "nk",
        "နက",
        "နခ"
    ]):
        temp += 10

    if any(k in clean_line for k in [
        "ဆယ်ပြည့်",
        "ဆယ်ပြည်"
    ]):
        temp += 10

    if any(k in clean_line for k in [
        "အပူးစုံ",
        "အပူး"
    ]):
        temp += 10

    if any(k in clean_line for k in [
        "စုံဘရိတ်",
        "စုံbk",
        "မbk",
        "မဘရိတ်"
    ]):
        temp += 50

    if any(k in clean_line for k in [
        "စစ",
        "မမ",
        "စမ",
        "မစ",
        "စုံစုံ",
        "စုံမ"
    ]):

        temp += 50 if is_r else 25

    if temp > 0:
        return temp * amount

    # --------------------------------
    # DIRECT 2D
    # --------------------------------

    if pairs:

        # 12r500
        r_match = re.search(r'(\d+)r(\d+)', original)

        if r_match:

            r_amount = int(r_match.group(2))

            return (len(pairs) * amount) + (
                len(pairs) * r_amount
            )

        if is_r:
            return len(pairs) * 2 * amount

        return len(pairs) * amount

    return 0


# =========================
# TELEGRAM HANDLER
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return

    text = update.message.text.strip()

    username = (
        f"@{update.message.from_user.username}"
        if update.message.from_user.username
        else update.message.from_user.first_name
    )

    lines = text.split("\n")

    default_amount = 100
    commission_percent = 0

    # =========================
    # DEFAULTS
    # =========================

    for line in lines:

        line = normalize_text(line)

        percent_match = re.search(r'(\d+)\s*%', line)

        if percent_match:
            commission_percent = int(
                percent_match.group(1)
            )

        amount_match = re.search(r'(\d+)\s*$', line)

        if amount_match:
            default_amount = int(
                amount_match.group(1)
            )

    # =========================
    # CALCULATE
    # =========================

    grand_total = 0

    for line in lines:

        try:
            grand_total += calculate_line_logic(
                line,
                default_amount
            )

        except Exception as e:
            print("ERROR:", e)

    if grand_total <= 0:
        return

    commission = (
        grand_total * commission_percent
    ) // 100

    final_total = grand_total - commission

    # =========================
    # RESPONSE
    # =========================

    response = (
        f"👤 {username}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 စုစုပေါင်း = {grand_total:,} ကျပ်\n"
    )

    if commission_percent > 0:

        response += (
            f"📉 ကော်မရှင် ({commission_percent}%)"
            f" = {commission:,} ကျပ်\n"
        )

        response += (
            f"✅ လက်ကျန် = "
            f"{final_total:,} ကျပ်\n"
        )

    response += "━━━━━━━━━━━━━━\n🍀 ကံကောင်းပါစေ"

    await update.message.reply_text(response)


# =========================
# RUN BOT
# =========================

if __name__ == "__main__":

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("BOT RUNNING...")

    app.run_polling()
