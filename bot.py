import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)

# =========================================
# BOT TOKEN
# =========================================

TOKEN = "YOUR_BOT_TOKEN"

# =========================================
# 2D NAME
# =========================================

TWO_D_NAMES = {
    "Dubai": ["du", "dubai", "ဒူ", "ဒူဘိုင်း"],
    "Mega": ["me", "mega", "မီ", "မီဂါ"],
    "Maxi": ["maxi", "max", "မက်ဆီ", "မက်စီ", "စီစီ"],
    "Global": ["glo", "global", "ဂလို"],
    "London": ["landon", "london", "လန်လန်", "လန်ဒန်", "ld"],
    "Lao": ["lao", "loa", "loadon", "laodon", "လာလာ", "လာအို", "laos", "loas"],
    "Mm": ["mm"]
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

    # separator
    text = text.replace("*", " ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("=", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================
# GET DEFAULT AMOUNT
# =========================================

def get_default_amount(lines):

    for line in reversed(lines):

        nums = re.findall(r"\d+", line)

        if nums:
            return int(nums[-1])

    return 0


# =========================================
# COUNT DIRECT NUMBERS
# =========================================

def count_direct_numbers(line):

    nums = re.findall(r"\b\d{2}\b", line)

    return len(nums)


# =========================================
# MAIN CALCULATOR
# =========================================

def calculate_line(line, default_amount):

    original = line
    line = normalize(line)

    # -------------------------------------
    # amount
    # -------------------------------------

    amount = default_amount

    r_amount = None

    # 23 45 56=500R250
    r_match = re.search(r"r\s*(\d+)", original.lower())

    if r_match:
        r_amount = int(r_match.group(1))

    nums = re.findall(r"\d+", original)

    if nums:

        last_num = int(nums[-1])

        # amount detect
        if last_num >= 10:
            amount = last_num

    # -------------------------------------
    # keywords
    # -------------------------------------

    total_boxes = 0

    # =====================================
    # 1. ပတ်ပူး / 20
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

        digits = re.findall(r"\d", line)

        total_boxes += len(digits) * 20

    # =====================================
    # 2. ပတ် / 19
    # =====================================

    elif any(x in line for x in [
        "ပတ်",
        "အပါ",
        "ပါ",
        "ch",
        "p"
    ]):

        digits = re.findall(r"\d", line)

        total_boxes += len(digits) * 19

    # =====================================
    # 3. ထိပ် / ပိတ်
    # =====================================

    elif any(x in line for x in [
        "ထိပ်",
        "ထိပ်စီး",
        "ထ",
        "top",
        "t"
    ]):

        digits = re.findall(r"\d", line)

        total_boxes += len(digits) * 10

    elif any(x in line for x in [
        "ပိတ်",
        "အပိတ်",
        "နောက်",
        "န",
        "ပ"
    ]):

        digits = re.findall(r"\d", line)

        total_boxes += len(digits) * 10

    # =====================================
    # 4. စုံဘရိတ်
    # =====================================

    elif any(x in line for x in [
        "စုံဘရိတ်",
        "စုံbk",
        "မbk",
        "စုံbk",
        "မဘရိတ်",
        "စဘရိတ်"
    ]):

        total_boxes += 50

    # =====================================
    # 5. ဘရိတ်
    # =====================================

    elif any(x in line for x in [
        "ဘရိတ်",
        "bk"
    ]):

        digits = re.findall(r"\d", line)

        total_boxes += len(digits) * 10

    # =====================================
    # 6. ခွေပူး
    # =====================================

    elif any(x in line for x in [
        "ခွေပူး",
        "အခွေပူး",
        "အပူးပါ",
        "အပူးအပြီးပါ"
    ]):

        digits = "".join(re.findall(r"\d", line))

        n = len(digits)

        total_boxes += n * n

    # =====================================
    # 7. ခွေ
    # =====================================

    elif any(x in line for x in [
        "ခွေ",
        "အခွေ",
        "ခ"
    ]):

        digits = "".join(re.findall(r"\d", line))

        n = len(digits)

        total_boxes += n * (n - 1)

    # =====================================
    # 8. ဆယ်ပြည့်
    # =====================================

    elif any(x in line for x in [
        "ဆယ်ပြည့်",
        "ဆယ်ပြည်",
        "ဆယ့်ပြည်"
    ]):

        total_boxes += 10

    # =====================================
    # 9. စုံပူး / မပူး
    # =====================================

    elif any(x in line for x in [
        "စုံပူး",
        "မပူး"
    ]):

        total_boxes += 5

    # =====================================
    # 10. အပူး
    # =====================================

    elif any(x in line for x in [
        "အပူး",
        "ပူး"
    ]):

        total_boxes += 10

    # =====================================
    # 11. စမ
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

        total_boxes += 25

        if "r" in line:
            total_boxes *= 2

    # =====================================
    # 12. ကပ်
    # =====================================

    elif "ကပ်" in line or "ကို" in line:

        parts = re.findall(r"\d+", line)

        if len(parts) >= 2:

            a = len(parts[0])
            b = len(parts[1])

            total_boxes += a * b

            if "r" in line:
                total_boxes *= 2

    # =====================================
    # 13. ပါဝါ
    # =====================================

    if any(x in line for x in [
        "ပါဝါ",
        "ပဝ",
        "pw",
        "power"
    ]):

        total_boxes += 10

    # =====================================
    # 14. နက္ခတ်
    # =====================================

    if any(x in line for x in [
        "နက္ခတ်",
        "nk",
        "နက",
        "နခ"
    ]):

        total_boxes += 10

    # =====================================
    # 15. ညီကို
    # =====================================

    if any(x in line for x in [
        "ညီကို",
        "ညီအကို",
        "ညီအစ်ကို"
    ]):

        total_boxes += 20

    # =====================================
    # 16. DIRECT / R
    # =====================================

    if total_boxes == 0:

        direct_count = count_direct_numbers(original)

        # 23 45 56=500R250
        if r_amount:

            normal_amount_match = re.search(
                r"[=\s](\d+)\s*r",
                original.lower()
            )

            if normal_amount_match:

                normal_amount = int(
                    normal_amount_match.group(1)
                )

            else:
                normal_amount = amount

            return (
                direct_count * normal_amount
            ) + (
                direct_count * r_amount
            )

        # 12r500
        elif "r" in line:

            return direct_count * amount * 2

        else:

            return direct_count * amount

    # =====================================
    # FINAL
    # =====================================

    return total_boxes * amount


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

    total = 0

    for line in lines:

        try:

            total += calculate_line(
                line,
                default_amount
            )

        except Exception as e:

            print("ERROR :", e)

    two_d_name = get_2d_name(text)

    # =====================================
    # REPLY
    # =====================================

    if total > 0:

        reply = (
            f"👤 {username}\n"
            f"--------------------\n"
            f"{two_d_name} စုစုပေါင်း = {total:,} ကျပ်\n"
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
