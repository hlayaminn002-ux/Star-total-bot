import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o" # သင့် Bot Token ကို ဒီမှာထည့်ပါ

# --- LOGIC FUNCTIONS ---
def get_2d_name(text):
    names = {
        'Dubai': ['du', 'dubai', 'ဒူ', 'ဒူဘိုင်း'],
        'Mega': ['me', 'mega', 'မီ', 'မီဂါ'],
        'Maxi': ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ'],
        'Global': ['glo', 'global', 'ဂလို'],
        'London': ['landon', 'london', 'လန်လန်', 'လန်ဒန်', 'ld'],
        'Lao': ['lao', 'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို', 'laos', 'loas'],
        'Mm': ['mm']
    }
    text_lower = text.lower()
    for name, keywords in names.items():
        if any(kw in text_lower for kw in keywords):
            return name
    return "2D"

def extract_amount(line):
    # စာကြောင်းရဲ့ အဆုံးမှာပါတဲ့ ဂဏန်းကို ရှာခြင်း
    match = re.search(r'(\d+)$', line.strip())
    return int(match.group(1)) if match else None

def calculate_line(line, default_amount):
    line = line.replace('-', ' ').replace('=', ' ').replace('*', ' ').replace('/', ' ').lower()
    amount_match = re.search(r'(\d+)$', line)
    amount = int(amount_match.group(1)) if amount_match else default_amount
    
    if not amount: return 0
    
    # 1. ပတ်သီး/အပါ (၁၉ ကွက်)
    if any(x in line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
        nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
        return len(nums) * 19 * amount

    # 2. ပတ်ပူး/၂၀ကွက်
    if any(x in line for x in ['ပတ်ပူး', 'ပူးပို', 'ထန', 'ထပ']):
        nums = re.findall(r'\d', line)
        return len(nums) * 20 * amount

    # 3. ထိပ်စီး/အပိတ် (၁၀ ကွက်)
    if any(x in line for x in ['ထိပ်', 'top', 't', 'ပိတ်', 'နောက်', 'န']):
        nums = re.findall(r'\d', line)
        return len(nums) * 10 * amount

    # 4. ခွေ/ခွေပူး
    if 'ခွေ' in line or 'ခ' in line:
        nums = re.findall(r'\d', line.split('ခ')[0])
        n = len(nums)
        if any(x in line for x in ['ပူး', 'အပြီးပါ']):
            return (n * n) * amount
        return (n * (n - 1)) * amount

    # 5. ဘရိတ်/အပူး/ပါဝါ/နက္ခတ် (၁၀ ကွက်)
    if any(x in line for x in ['ဘရိတ်', 'bk', 'အပူး', 'ပူး', 'ပါဝါ', 'pw', 'နက္ခတ်', 'nk']):
        if 'စုံပူး' in line or 'မပူး' in line: return 5 * amount
        return 10 * amount

    # 6. ညီကို (၂၀ ကွက်)
    if 'ညီကို' in line or 'ညီအကို' in line:
        return 20 * amount

    # 7. စုံမ/စမ (၂၅ ကွက်)
    if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
        res = 25 * amount
        return res * 2 if 'r' in line else res

    # 8. ကပ်/ကို (n x n)
    if 'ကပ်' in line or 'ကို' in line:
        parts = re.findall(r'(\d+)', line)
        if len(parts) >= 2:
            res = len(parts[0]) * len(parts[1]) * amount
            return res * 2 if 'r' in line else res

    # 9. ဒဲ့ / R
    digits = re.findall(r'\b\d{2}\b', line)
    if digits:
        total = 0
        if 'r' in line:
            # 23 45=500R250 ပုံစံတွက်ခြင်း
            r_parts = line.split('r')
            main_amt = extract_amount(r_parts[0]) or amount
            r_amt = int(r_parts[1]) if len(r_parts) > 1 and r_parts[1].isdigit() else main_amt
            total = (len(digits) * main_amt) + (len(digits) * r_amt)
        else:
            total = len(digits) * amount
        return total

    return 0

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    
    lines = text.strip().split('\n')
    
    # နောက်ဆုံးစာကြောင်းက amount ကိုရှာ
    default_amount = 0
    for line in reversed(lines):
        amt = extract_amount(line)
        if amt:
            default_amount = amt
            break
            
    name_2d = get_2d_name(text)
    grand_total = 0
    
    for line in lines:
        grand_total += calculate_line(line, default_amount)
    
    if grand_total > 0:
        response = f"👤 {username}\n"
        response += "--------------------\n"
        response += f"{name_2d} စုစုပေါင်း = {grand_total:,} ကျပ်\n"
        response += "ကံကောင်းပါစေရှင့်"
        
        # Reply ထောက်ပြီး ပြန်ခြင်း
        await update.message.reply_text(response)

# --- MAIN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling()
  
