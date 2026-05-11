import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o" # လူကြီးမင်း၏ Token ထည့်ပါ

def get_2d_name(text):
    names = {
        'Dubai': ['dubai', 'du', 'ဒူဘိုင်း', 'ဒူ'],
        'Mega': ['mega', 'me', 'မီဂါ', 'မီ'],
        'Maxi': ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ'],
        'Global': ['global', 'glo', 'ဂလို'],
        'London': ['london', 'landon', 'လန်ဒန်', 'ld'],
        'Lao': ['lao', 'laos', 'လာအို', 'လာလာ'],
        'Mm': ['mm']
    }
    text_lower = text.lower()
    for name, keywords in names.items():
        if any(kw in text_lower for kw in keywords):
            return name, keywords
    return "2D", []

def extract_amount(line):
    # စာကြောင်းအဆုံးမှ amount ကို ရှာသည်
    match = re.search(r'(\d+)\s*$', line.strip())
    return int(match.group(1)) if match else None

def calculate_line_logic(line, default_amount):
    line = line.lower().strip()
    if not line: return 0
    
    # % နုတ်တဲ့စာကြောင်းဆိုရင် ကျော်သွားမယ် (grand_total ထဲမပေါင်းရန်)
    if '%' in line: return 0

    # Amount ခွဲထုတ်ခြင်း
    amount = extract_amount(line) or default_amount
    if not amount: return 0

    # Amount ကို ဖယ်ပြီး ကျန်တဲ့စာသားကိုပဲ Logic စစ်မယ်
    clean_line = re.sub(r'\d+\s*$', '', line).strip()
    
    line_spots = 0
    is_r = any(x in clean_line for x in ['r', 'အာ'])

    # --- Logic များ စစ်ဆေးခြင်း ---
    
    # ၁။ ပါဝါ၊ ညီကို၊ အပူးစုံ၊ ဆယ်ပြည့်၊ နက္ခတ်၊ စုံမဘရိတ် (Multi-Keyword Support)
    if any(x in clean_line for x in ['ပါဝါ', 'pw', 'power']): line_spots += 10
    if any(x in clean_line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): line_spots += 20
    if any(x in clean_line for x in ['နက္ခတ်', 'nk', 'နက', 'နခ', 'နတ်']): line_spots += 10
    if any(x in clean_line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်']): line_spots += 10
    if any(x in clean_line for x in ['အပူးစုံ', 'အပူး', 'ပူး']) and 'ခွေ' not in clean_line: line_spots += 10
    if any(x in clean_line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']): line_spots += 50

    # ၂။ ပတ်သီး (19 ကွက်) / ပတ်ပူး (20 ကွက်)
    digits = re.findall(r'\b\d\b', clean_line) # ဂဏန်းတစ်လုံးချင်းစီကို ရှာ
    if any(x in clean_line for x in ['ပတ်ပူး', 'ပူးပို', 'ထိပ်နောက်']):
        line_spots += len(digits) * 20
    elif any(x in clean_line for x in ['ပတ်', 'အပါ', 'ပါ']):
        line_spots += len(digits) * 19

    # ၃။ ထိပ်စီး / အပိတ် / ဘရိတ် (10 ကွက်)
    elif any(x in clean_line for x in ['ထိပ်', 'ပိတ်', 'နောက်', 'ဘရိတ်', 'bk']):
        line_spots += (len(digits) if digits else len(re.findall(r'\d{2}', clean_line))) * 10

    # ၄။ ခွေ (n*n-1) နှင့် ခွေပူး (n*n)
    elif 'ခွေ' in clean_line or 'ခ' in clean_line:
        nums = re.search(r'(\d+)', clean_line)
        if nums:
            n = len(nums.group(1))
            if any(x in clean_line for x in ['ပူး', 'အပူးပါ', 'အပြီးပါ']):
                line_spots += (n * n)
            else:
                line_spots += (n * (n - 1))

    # ၅။ စစ / မမ / စမ / မစ (25 ကွက်)
    elif any(x in clean_line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
        line_spots += 50 if is_r else 25

    # ၆။ ကပ် / ကို (n1 * n2)
    elif any(x in clean_line for x in ['ကပ်', 'ကို']):
        parts = re.findall(r'(\d+)', clean_line)
        if len(parts) >= 2:
            base = len(parts[0]) * len(parts[1])
            line_spots += base * (2 if is_r else 1)

    # ၇။ ဒဲ့ဂဏန်းများ (12 34 56)
    else:
        two_digits = re.findall(r'\b\d{2}\b', clean_line)
        if two_digits:
            # 500R250 Special Case
            if 'r' in line:
                r_match = re.search(r'r(\d+)$', line)
                if r_match:
                    r_amt = int(r_match.group(1))
                    return (len(two_digits) * amount) + (len(two_digits) * r_amt)
            line_spots += len(two_digits) * (2 if is_r else 1)

    return line_spots * amount

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    text = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    
    name_2d, name_kws = get_2d_name(text)
    lines = text.strip().split('\n')
    
    # ၁။ Default Amount နှင့် % ရှာခြင်း
    default_amount = 0
    comm_percent = 0
    for line in lines:
        amt = extract_amount(line)
        if amt and not default_amount: default_amount = amt
        if '%' in line:
            perc_match = re.search(r'(\d+)\s*%', line)
            if perc_match: comm_percent = int(perc_match[1])

    # ၂။ တွက်ချက်ခြင်း
    grand_total = 0
    for line in lines:
        grand_total += calculate_line_logic(line, default_amount)
    
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
        response += f"🍀 {name_2d} ကံကောင်းပါစေရှင့်"
        await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling()
    
