import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o"

# --- HELPER FUNCTIONS ---
def get_2d_name(text):
    # နာမည်များကို အရင်ရှာပြီး တွက်ချက်မှုထဲမပါအောင် ဖယ်ထုတ်ရန်
    names = {
        'Dubai': ['dubai', 'du', 'ဒူဘိုင်း', 'ဒူ'],
        'Mega': ['mega', 'me', 'မီဂါ', 'မီ'],
        'Maxi': ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ'],
        'Global': ['global', 'glo', 'ဂလို'],
        'London': ['london', 'landon', 'လန်ဒန်', 'လန်လန်', 'ld'],
        'Lao': ['lao', 'laos', 'loa', 'လာအို', 'လာလာ', 'loadon'],
        'Mm': ['mm']
    }
    text_lower = text.lower()
    for name, keywords in names.items():
        if any(kw in text_lower for kw in keywords):
            return name, keywords
    return "2D", []

def extract_amount(line):
    # စာကြောင်းရဲ့ အဆုံးမှာပါတဲ့ amount ကို ရှာခြင်း
    match = re.search(r'(\d+)\s*$', line.strip())
    return int(match.group(1)) if match else None

def calculate_line_logic(line, default_amount):
    # စာသားသန့်စင်ခြင်း (သင်္ကေတများကို space ပြောင်းသည်)
    line = line.lower()
    clean_line = re.sub(r'[-=*+/]', ' ', line)
    
    amount = extract_amount(line) or default_amount
    if not amount: return 0

    total_spots = 0
    
    # ၁။ ပတ်ပူး / ၂၀ကွက် (၂၀ ကွက်တွက်နည်း)
    pb_kws = ['ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']
    for kw in pb_kws:
        if kw in clean_line:
            nums = re.findall(r'\d', clean_line.split(kw)[0])
            total_spots += len(nums) * 20
            return total_spots * amount

    # ၂။ ပတ်သီး / အပါ / ပါ / Ch / P (၁၉ ကွက်တွက်နည်း)
    p_kws = ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']
    for kw in p_kws:
        if kw in clean_line:
            nums = re.findall(r'\d', clean_line.split(kw)[0])
            total_spots += len(nums) * 19
            return total_spots * amount

    # ၃။ ထိပ် / Top / T (၁၀ ကွက်)
    if any(x in clean_line for x in ['ထိပ်', 'top', 't']):
        nums = re.findall(r'\d', clean_line.split('ထ')[0] if 'ထ' in clean_line else clean_line)
        total_spots += len(nums) * 10
        return total_spots * amount

    # ၄။ ပိတ် / အပိတ် / နောက် / န / ပ (၁၀ ကွက်)
    if any(x in clean_line for x in ['ပိတ်', 'အပိတ်', 'နောက်', 'န', 'ပ']):
        nums = re.findall(r'\d', clean_line.split('ပ')[0] if 'ပ' in clean_line else clean_line)
        total_spots += len(nums) * 10
        return total_spots * amount

    # ၅။ ဘရိတ် / Bk (၁၀ ကွက်)
    if any(x in clean_line for x in ['ဘရိတ်', 'bk']):
        nums = re.findall(r'\d', clean_line.split('ဘ')[0] if 'ဘ' in clean_line else clean_line)
        total_spots += len(nums) * 10
        return total_spots * amount

    # ၆။ ခွေ (n * n-1) နှင့် ခွေပူး (n * n)
    if 'ခွေ' in clean_line or 'ခ' in clean_line:
        match = re.search(r'(\d+)', clean_line)
        if match:
            n = len(match.group(1))
            if any(x in clean_line for x in ['ပူး', 'အပူးပါ', 'အပြီးပါ']):
                total_spots += (n * n)
            else:
                total_spots += (n * (n - 1))
        return total_spots * amount

    # ၇။ အထူး Keywords (စုံမ၊ ပါဝါ၊ နက္ခတ်၊ ညီကို)
    if any(x in clean_line for x in ['ပါဝါ', 'ပဝ', 'pw', 'power']): total_spots += 10
    if any(x in clean_line for x in ['နက္ခတ်', 'nk', 'နက', 'နခ']): total_spots += 10
    if any(x in clean_line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): total_spots += 20
    if any(x in clean_line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']): total_spots += 10
    if any(x in clean_line for x in ['အပူးစုံ', 'အပူး', 'ပူး']):
        if 'စုံပူး' in clean_line or 'မပူး' in clean_line: total_spots += 5
        else: total_spots += 10
    if any(x in clean_line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']): total_spots += 25
    if any(x in clean_line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်']): total_spots += 50
    
    # ၈။ ကပ် / ကို (n * n)
    if 'ကပ်' in clean_line or 'ကို' in clean_line:
        parts = re.findall(r'(\d+)', clean_line)
        if len(parts) >= 2:
            res = len(parts[0]) * len(parts[1])
            if 'r' in clean_line: return (res * 2) * amount
            return res * amount

    # ၉။ ဒဲ့ဂဏန်းများ နှင့် R Logic (ဥပမာ- 12 34 R500)
    digits = re.findall(r'\b\d{2}\b', clean_line)
    if digits:
        if 'r' in clean_line or 'အာ' in clean_line:
            # ဒဲ့ + R ခွဲတွက်တာ (500R250) ရှိမရှိ စစ်သည်
            r_split = clean_line.split('r')
            if len(r_split) > 1 and re.search(r'\d', r_split[1]):
                main_amt = extract_amount(r_split[0]) or amount
                r_amt = extract_amount(r_split[1])
                return (len(digits) * main_amt) + (len(digits) * r_amt)
            else:
                return (len(digits) * 2) * amount
        else:
            return len(digits) * amount

    return total_spots * (2 * amount if 'r' in clean_line else amount)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    original_text = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    
    # ၁။ နာမည်ရှာပြီး ဖယ်ထုတ်သည်
    name_2d, name_kws = get_2d_name(original_text)
    temp_text = original_text.lower()
    for kw in name_kws:
        temp_text = temp_text.replace(kw, "")
    
    lines = temp_text.strip().split('\n')
    
    # ၂။ Default Amount ကို အောက်ဆုံးစာကြောင်းမှ ယူသည်
    default_amount = 0
    for line in reversed(lines):
        amt = extract_amount(line)
        if amt:
            default_amount = amt
            break
            
    # ၃။ တစ်ကြောင်းချင်းတွက်ချက်သည်
    grand_total = 0
    for line in lines:
        if line.strip():
            grand_total += calculate_line_logic(line, default_amount)
    
    if grand_total > 0:
        response = f"👤 {username}\n"
        response += "--------------------\n"
        response += f"{name_2d} စုစုပေါင်း = {grand_total:,} ကျပ်\n"
        response += "ကံကောင်းပါစေရှင့်"
        await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
    
