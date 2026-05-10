# =========================================
# 2D CALCULATOR TELEGRAM BOT
# =========================================

import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================================
# TOKEN
# =========================================

TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o"

# =========================================
# 2D NAME LIST
# =========================================

TWO_D_NAMES = {
    "Dubai": [
        "du", "dubai", "ဒူ", "ဒူဘိုင်း"
    ],

    "Mega": [
        "me", "mega", "မီ", "မီဂါ"
    ],

    "Maxi": [
        "maxi", "max",
        "မက်ဆီ", "မက်စီ", "စီစီ"
    ],

    "Global": [
        "glo", "global", "ဂလို"
    ],

    "London": [
        "landon", "london",
        "လန်လန်", "လန်ဒန်",
        "ld"
    ],

    "Lao": [
        "lao", "loa",
        "loadon", "laodon",
        "လာလာ", "လာအို",
        "laos", "loas"
    ],

    "Mm": [
        "mm"
    ]
}

# =========================================
# GET 2D NAME
# =========================================

def get_2d_name(text):

    text = text.lower()

    for name, keys in TWO_D_NAMES.items():

        for key in keys:

            if key.lower() in text:
                return name

    return "2D"

# =========================================
# NORMALIZE
# =========================================

def normalize(text):

    text = text.lower()

    text = text.replace("*", " ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("=", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()

# =========================================
# DEFAULT AMOUNT
# =========================================

def get_default_amount(lines):

    for line in reversed(lines):

        nums = re.findall(r"\d+", line)

        if nums:

            last_num = int(nums[-1])

            if last_num >= 10:
                return last_num

    return 100

# =========================================
# 2D NUMBER COUNT
# =========================================

def count_2d(line):

    nums = re.findall(r"\b\d{2}\b", line)

    return len(nums)

# =========================================
# MAIN CALCULATOR
# =========================================

def calculate_line(line, default_amount):

    original = line
    line = normalize(line)

    amount = default_amount

    total_box = 0

    # =====================================
    # R AMOUNT
    # =====================================

    r_amount = None

    r_match = re.search(r"r\s*(\d+)", original.lower())

    if r_match:
        r_amount = int(r_match.group(1))

    # =====================================
    # NORMAL AMOUNT
    # =====================================

    nums = re.findall(r"\d+", original)

    if nums:

        last_num = int(nums[-1])

        if last_num >= 10:
            amount = last_num

    # =====================================
    # DIGIT COUNT
    # =====================================

    digits = re.findall(r"\d", line)

    digit_count = len(digits)

    # =====================================
    # ပတ်ပူး
    # =====================================

    if any(x in line for x in [
        "ပတ်ပူး",
        "ပူးပို",
        "ပတ်ပူးပို",
        "ပတ်အကွက်20",
        "ထန",
        "ထပ",
        "ထိပ်ပိတ်",
        "ထိပ်နောက်"
    ]):

        total_box += digit_count * 20

    # =====================================
    # ပတ်
    # =====================================

    elif any(x in line for x in [
        "ပတ်",
        "အပါ",
        "ပါ",
        "ch",
        "p"
    ]):

        total_box += digit_count * 19

    # =====================================
    # ထိပ်
    # =====================================

    elif any(x in line for x in [
        "ထိပ်",
        "ထိပ်စီး",
        "ထ",
        "top",
        "t"
    ]):

        total_box += digit_count * 10

    # =====================================
    # ပိတ်
    # =====================================

    elif any(x in line for x in [
        "ပိတ်",
        "အပိတ်",
        "နောက်",
        "န",
        "ပ"
    ]):

        total_box += digit_count * 10

    # =====================================
    # စုံဘရိတ်
    # =====================================

    elif any(x in line for x in [
        "စုံဘရိတ်",
        "စုံbk",
        "မbk",
        "စုံbk",
        "မဘရိတ်",
        "စဘရိတ်"
    ]):

        total_box += 50

    # =====================================
    # ဘရိတ်
    # =====================================

    elif any(x in line for x in [
        "ဘရိတ်",
        "bk"
    ]):

        total_box += digit_count * 10

    # =====================================
    # ခွေပူး
    # =====================================

    elif any(x in line for x in [
        "ခွေပူး",
        "အခွေပူး",
        "အပူးပါ",
        "အပူးအပြီးပါ"
    ]):

        pure_digits = "".join(re.findall(r"\d", line))

        n = len(pure_digits)

        total_box += n * n

    # =====================================
    # ခွေ
    # =====================================

    elif any(x in line for x in [
        "ခွေ",
        "အခွေ",
        "ခ"
    ]):

        pure_digits = "".join(re.findall(r"\d", line))

        n = len(pure_digits)

        total_box += n * (n - 1)

    # =====================================
    # ဆယ်ပြည့်
    # =====================================

    elif any(x in line for x in [
        "ဆယ်ပြည့်",
        "ဆယ်ပြည်",
        "ဆယ့်ပြည်"
    ]):

        total_box += 10

    # =====================================
    # စုံပူး
    # =====================================

    elif any(x in line for x in [
        "စုံပူး",
        "မပူး"
    ]):

        total_box += 5

    # =====================================
    # အပူး
    # =====================================

    elif any(x in line for x in [
        "အပူး",
        "ပူး"
    ]):

        total_box += 10

    # =====================================
    # စမ
    # =====================================

    elif any(x in line for x in [
        "စစ",
        "မမ",
        "စမ",
        "မစ",
        "စုံစုံ",
        "စုံမ",
        "စုူံစူံ",
        "စူံစုံ",
        "စုံစူံ"
    ]):

        total_box += 25

        if "r" in line:
            total_box *= 2

    # =====================================
    # ကပ်
    # =====================================

    elif "ကပ်" in line or "ကို" in line:

        parts = re.findall(r"\d+", line)

        if len(parts) >= 2:

            a = len(parts[0])
            b = len(parts[1])

            total_box += a * b

            if "r" in line:
                total_box *= 2

    # =====================================
    # ပါဝါ
    # =====================================

    if any(x in line for x in [
        "ပါဝါ",
        "ပဝ",
        "pw",
        "power"
    ]):

        total_box += 10

    # =====================================
    # နက္ခတ်
    # =====================================

    if any(x in line for x in [
        "နက္ခတ်",
        "nk",
        "နက",
        "နခ"
    ]):

        total_box += 10

    # =====================================
    # ညီကို
    # =====================================

    if any(x in line for x in [
        "ညီကို",
        "ညီအကို",
        "ညီအစ်ကို"
    ]):

        total_box += 20

    # =====================================
    # DIRECT / R
    # =====================================

    if total_box == 0:

        direct_count = count_2d(original)

        # 23 45 56=500R250

        if r_amount:

            normal_amount = amount

            normal_match = re.search(
                r"[=\s](\d+)\s*r",
                original.lower()
            )

            if normal_match:

                normal_amount = int(
                    normal_match.group(1)
                )

            total = (
                direct_count * normal_amount
            ) + (
                direct_count * r_amount
            )

            return total

        # 12R500

        elif "r" in line:

            return direct_count * amount * 2

        # direct

        else:

            return direct_count * amount

    # =====================================
    # FINAL
    # =====================================

    return total_box * amount

# =========================================
# HANDLE MESSAGE
# =========================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    user = update.message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    lines = text.split("\n")

    default_amount = get_default_amount(lines)

    grand_total = 0

    for line in lines:

        try:

            grand_total += calculate_line(
                line,
                default_amount
            )

        except Exception as e:

            print("ERROR :", e)

    two_d_name = get_2d_name(text)

    # =====================================
    # REPLY
    # =====================================

    if grand_total > 0:

        reply = (
            f"👤 {username}\n\n"
            f"{two_d_name} စုစုပေါင်း = "
            f"{grand_total:,} ကျပ်\n"
            f"ကံကောင်းပါစေရှင့်"
        )

        await update.message.reply_text(
            reply,
            reply_to_message_id=update.message.message_id
        )

# =========================================
# MAIN
# =========================================

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
