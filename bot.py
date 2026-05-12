import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o"

def calculate_line_logic(line, default_amount):
    line = line.lower().strip()
    if not line or '%' in line: return 0

    # 1. Amount ခွဲထုတ်ခြင်း (ဥပမာ- 123ခွေ 500 သို့မဟုတ် 12r10)
    match = re.search(r'(\d+)\s*$', line)
    amount = int(match.group(1)) if match else default_amount
    if not amount: return 0

    # Amount ကိုဖယ်ပြီး ကျန်တဲ့စာသားကိုပဲ စစ်မယ်
    clean_line = re.sub(r'\d+\s*$', '', line).strip()
    is_r = any(x in clean_line for x in ['r', 'အာ'])
    line_spots = 0

    # --- [ဦးစားပေးအလိုက် Logic စစ်ဆေးခြင်း] ---

    # (A) Multi-Keyword Group (ပေါင်းတွက်ရမည့် Keywords များ)
    if any(x in clean_line for x in ['ပါဝါ', 'pw', 'power']): line_spots += 10
    if any(x in clean_line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): line_spots += 20
    if any(x in clean_line for x in ['နက္ခတ်', 'nk', 'နက', 'နခ', 'နတ်']): line_spots += 10
    if any(x in clean_line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်']): line_spots += 10
    if any(x in clean_line for x in ['အပူးစုံ', 'အပူး', 'ပူး']) and not any(k in clean_line for k in ['ခွေ', 'ပတ်', 'စုံ']): 
        line_spots += 10
    if any(x in clean_line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']): line_spots += 50

    # (B) ခွေ / ခွေပူး Logic (ခွေပူးကို အရင်စစ်ရမည်)
    if 'ခွေ' in clean_line or 'ခ' in clean_line:
        nums = re.search(r'(\d+)', clean_line)
        if nums:
            n = len(nums.group(1))
            if any(x in clean_line for x in ['ပူး', 'အပူးပါ', 'အပြီးပါ']):
                return (n * n) * amount # ခွေပူး (n*n)
            else:
                return (n * (n - 1)) * amount # ခွေ (n*n-1)

    # (C) ကပ် / ကို Logic
    if any(x in clean_line for x in ['ကပ်', 'ကို']):
        parts = re.findall(r'(\d+)', clean_line)
        if len(parts) >= 2:
            base = len(parts[0]) * len(parts[1])
            return base * (2 if is_r else 1) * amount

    # (D) ပတ်သီး / ထိပ်နောက် Logic
    digits = re.findall(r'\b\d\b', clean_line) # ဂဏန်းတစ်လုံးချင်းစီ
    if any(x in clean_line for x in ['ပတ်ပူး', 'ပူးပို', 'ထိပ်နောက်', 'ထန']):
        return len(digits) * 20 * amount
    if any(x in clean_line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
        return len(digits) * 19 * amount

    # (E) ထိပ်စီး / အပိတ် / ဘရိတ်
    if any(x in clean_line for x in ['ထိပ်', 'top', 't']):
        return (len(digits) if digits else 1) * 10 * amount
    if any(x in clean_line for x in ['ပိတ်', 'အပိတ်', 'နောက်', 'န']):
        return (len(digits) if digits else 1) * 10 * amount
    if any(x in clean_line for x in ['ဘရိတ်', 'bk']):
        return (len(digits) if digits else 1) * 10 * amount

    # (F) စစ / မမ / စမ / မစ
    if any(x in clean_line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
        return (50 if is_r else 25) * amount

    # (G) ဒဲ့ဂဏန်းများ (12 34 56)
    two_digits = re.findall(r'\b\d{2}\b', clean_line)
    if two_digits:
        # 500r250 စနစ်
        if 'r' in line:
            r_match = re.search(r'r(\d+)$', line)
            if r_match:
                r_amt = int(r_match.group(1))
                return (len(two_digits) * amount) + (len(two_digits) * r_amt)
        return len(two_digits) * (2 if is_r else 1) * amount

    return line_spots * amount

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name

    lines = text.strip().split('\n')
    
    # ၁။ Default Amount နှင့် % ရှာခြင်း
    default_amount = 0
    comm_percent = 0
    for line in lines:
        amt = extract_amount_via_regex(line)
        if amt and not default_amount: default_amount = amt
        if '%' in line:
            perc_match = re.search(r'(\d+)\s*%', line)
            if perc_match: comm_percent = int(perc_match[1])

    # ၂။ စုစုပေါင်းတွက်ခြင်း
    grand_total = sum(calculate_line_logic(line, default_amount) for line in lines)
    
    if grand_total > 0:
        comm_amount = (grand_total * comm_percent) // 100
        net_total = grand_total - comm_amount
        
        response = f"👤 {username}\n"
        response += "--------------------\n"
        response += f"💰 စုစုပေါင်း = {grand_total:,} ကျပ်\n"
        if comm_percent > 0:
            response += f"📉 ကော်မရှင် ({comm_percent}%) = {comm_amount:,} ကျပ်\n"
            response += f"✅ လက်ကျန် = {net_total:,} ကျပ်\n"
        response += "--------------------\n"
        response += "🍀 ကံကောင်းပါစေရှင့်"
        await update.message.reply_text(response)

def extract_amount_via_regex(line):
    match = re.search(r'(\d+)\s*$', line.strip())
    return int(match.group(1)) if match else None

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling()
    
