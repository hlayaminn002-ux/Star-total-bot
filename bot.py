import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================================
# CONFIG
# =========================================

TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o"

# =========================================
# 2D NAME
# =========================================

TWO_D_NAMES = {
    "Dubai": [
        "du", "dubai", "ဒူ", "ဒူဘိုင်း"
    ],

    "Mega": [
        "me", "mega", "မီ", "မီဂါ"
    ],

    "Maxi": [
        "maxi", "max", "မက်ဆီ", "မက်စီ", "စီစီ"
    ],

    "Global": [
        "glo", "global", "ဂလို"
    ],

    "London": [
        "landon", "london", "လန်လန်",
        "လန်ဒန်", "ld"
    ],

    "Lao": [
        "lao", "loa", "loadon",
        "laodon", "လာလာ", "လာအို",
        "laos", "loas"
    ],

    "Mm": [
        "mm"
    ]
}


def get_2d_name(text):
    text = text.lower()

    for name, keywords in TWO_D_NAMES.items():
        for kw in keywords:
            if kw.lower() in text:
                return name

    return "2D"


# =========================================
# NORMALIZE
# =========================================

def normalize_text(text):

    text = text.lower()

    separators = ["*", "/", "=", "-", ","]
    for s in separators:
        text = text.replace(s, " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================
# EXTRACT AMOUNT
# =========================================

def extract_amount(line):

    # R amount
    r_match = re.search(r"[rအာ](\d+)", line.lower())
    r_amount = int(r_match.group(1)) if r_match else None

    # normal amount
    all_nums = re.findall(r"\d+", line)

    amount = None

    if all_nums:
        amount = int(all_nums[-1])

    return amount, r_amount


# =========================================
# COUNT 2D NUMBERS
# =========================================

def get_2d_numbers(line):

    return re.findall(r"\b\d{2}\b", line)


# =========================================
# MAIN CALCULATOR
# =========================================

def calculate_line(line, default_amount):

    original = line
    line = normalize_text(line)

    total = 0

    amount, r_amount = extract_amount(original)

    if not amount:
        amount = default_amount

    if not amount:
        amount = 0

    # =====================================
    # DIGIT COUNT
    # =====================================

    digit_groups = re.findall(r"\d+", line)

    # =====================================
    # 1. ပတ်ပူး / 20
    # =====================================

    if any(x in line for x in [
        "ပတ်ပူး", "ပူးပို", "ပတ်အကွက်20",
        "ထန", "ထပ", "ထိပ်ပိတ်",
        "ထိပ်နောက်"
    ]):

        count = 0

        for d in digit_groups:
            count += len(d)

        return count * 20 * amount

    # =====================================
    # 2. ပတ် / 19
    # =====================================

    if any(x in line for x in [
        "ပတ်", "အပါ", "ပါ", "ch", "p"
    ]):

        count = 0

        for d in digit_groups:
            count += len(d)

        return count * 19 * amount

    # =====================================
    # 3. ထိပ် / TOP
    # =====================================

    if any(x in line for x in [
        "ထိပ်", "ထိပ်စီး", "top", "t"
    ]):

        count = 0

        for d in digit_groups:
            count += len(d)

        return count * 10 * amount

    # =====================================
    # 4. ပိတ်
    # =====================================

    if any(x in line for x in [
        "ပိတ်", "အပိတ်", "နောက်", "န", "ပ"
    ]):

        count = 0

        for d in digit_groups:
            count += len(d)

        return count * 10 * amount

    # =====================================
    # 5. စုံဘရိတ်
    # =====================================

    if any(x in line for x in [
        "စုံဘရိတ်",
        "စုံbk",
        "မbk",
        "စုံbk",
        "မဘရိတ်",
        "စဘရိတ်"
    ]):

        return 50 * amount

    # =====================================
    # 6. ဘရိတ်
    # =====================================

    if any(x in line for x in [
        "ဘရိတ်", "bk"
    ]):

        count = len(digit_groups)

        if count == 0:
            count = 1

        return count * 10 * amount

    # =====================================
    # 7. ခွေ ပူး
    # =====================================

    if any(x in line for x in [
        "ခွေပူး",
        "အခွေပူး",
        "အပူးပါ",
        "အပူးအပြီးပါ"
    ]):

        nums = "".join(digit_groups)

        n = len(nums)

        return (n * n) * amount

    # =====================================
    # 8. ခွေ
    # =====================================

    if any(x in line for x in [
        "ခွေ", "အခွေ", "ခ"
    ]):

        nums = "".join(digit_groups)

        n = len(nums)

        return (n * (n - 1)) * amount

    # =====================================
    # 9. ဆယ်ပြည့်
    # =====================================

    if any(x in line for x in [
        "ဆယ်ပြည့်",
        "ဆယ်ပြည်",
        "ဆယ့်ပြည်"
    ]):

        return 10 * amount

    # =====================================
    # 10. စုံပူး / မပူး
    # =====================================

    if any(x in line for x in [
        "စုံပူး",
        "မပူး"
    ]):

        return 5 * amount

    # =====================================
    # 11. အပူး
    # =====================================

    if any(x in line for x in [
        "အပူး",
        "ပူး"
    ]):

        return 10 * amount

    # =====================================
    # 12. စမ
    # =====================================

    if any(x in line for x in [
        "စစ",
        "မမ",
        "စမ",
        "မစ",
        "စုံစုံ",
        "စုံမ",
        "စုံစူံ",
        "စူံစုံ"
    ]):

        result = 25 * amount

        if "r" in line:
            result *= 2

        return result

    # =====================================
    # 13. ကပ်
    # =====================================

    if "ကပ်" in line or "ကို" in line:

        parts = re.findall(r"\d+", line)

        if len(parts) >= 2:

            a = len(parts[0])
            b = len(parts[1])

            result = a * b * amount

            if "r" in line:
                result *= 2

            return result

    # =====================================
    # 14. ပါဝါ
    # =====================================

    if any(x in line for x in [
        "ပါဝါ", "ပဝ", "pw", "power"
    ]):

        return 10 * amount

    # =====================================
    # 15. နက္ခတ်
    # =====================================

    if any(x in line for x in [
        "နက္ခတ်", "nk", "နက", "နခ"
    ]):

        return 10 * amount

    # =====================================
    # 16. ညီကို
    # =====================================

    if any(x in line for x in [
        "ညီကို",
        "ညီအကို",
        "ညီအစ်ကို"
    ]):

        return 20 * amount

    # =====================================
    # 17. ဒဲ့ / R
    # =====================================

    numbers = get_2d_numbers(original)

    if numbers:

        if r_amount:

            main_amount_match = re.search(
                r"=(\d+)",
                original
            )

            if main_amount_match:
                main_amount = int(main_amount_match.group(1))
            else:
                main_amount = amount

            total += len(numbers) * main_amount
            total += len(numbers) * r_amount

            return total

        elif "r" in line:

            return len(numbers) * amount * 2

        else:

            return len(numbers) * amount

    return 0


# =========================================
# TELEGRAM
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

    # =====================================
    # DEFAULT AMOUNT
    # =====================================

    default_amount = 0

    for line in reversed(lines):

        nums = re.findall(r"\d+", line)

        if nums:
            default_amount = int(nums[-1])
            break

    # =====================================
    # TOTAL
    # =====================================

    grand_total = 0

    for line in lines:

        try:
            grand_total += calculate_line(
                line,
                default_amount
            )

        except Exception as e:
            print("ERROR :", e)

    # =====================================
    # 2D NAME
    # =====================================

    two_d_name = get_2d_name(text)

    # =====================================
    # REPLY
    # =====================================

    if grand_total > 0:

        reply = (
            f"👤 {username}\n"
            f"--------------------\n"
            f"{two_d_name} Total =\n"
            f"--------------------\n"
            f"လွဲရမည့်ငွေ = {grand_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
            f"ကံကောင်းပါစေ နော်"
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
