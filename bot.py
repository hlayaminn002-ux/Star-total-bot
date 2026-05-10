import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o"

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
    # စာကြောင်းအဆုံးရှိ ဂဏန်းကို ရှာသည် (R ရဲ့နောက်က ဂဏန်းလည်း ဖြစ်နိုင်သည်)
    match = re.search(r'(\d+)\s*$', line.strip())
    if match:
        return int(match.group(1))
    return None

def calculate_line_logic(line, default_amount):
    # စာသားများကို သန့်စင်ခြင်း
    clean_line = line.replace('-', ' ').replace('=', ' ').replace('*', ' ').replace('/', ' ').lower()
    
    # Amount ရှာဖွေခြင်း
    line_amount = extract_amount(line) or default_amount
    if not line_amount: return 0

    total_spots = 0
    
    # 1. ပတ်သီး (၁၉ ကွက်)
    if any(x in clean_line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']) and 'ပူးပို' not in clean_line and 'အပူးပို' not in clean_line:
        nums = re.findall(r'\d', clean_line.split('ပတ်')[0] if 'ပတ်' in clean_line else clean_line)
        total_spots += len(nums) * 19
        
    # 2. ပတ်ပူး / ၂၀ကွက်
    elif any(x in clean_line for x in ['ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', '၂၀ကွက်', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
        nums = re.findall(r'\d', clean_line)
        total_spots += len(nums) * 20

    if any(x in clean_line for x in ['ထိပ်', 'top', 'ထိပ်စီး']):

    target = clean_line

    if 'ထိပ်' in clean_line:
        target = clean_line.split('ထိပ်')[0]

    elif 'top' in clean_line:
        target = clean_line.split('top')[0]

    nums = re.findall(r'\d', target)

    total_spots += len(nums) * 10

    # 4. အပိတ်/နောက် (၁၀ ကွက်)
    elif any(x in clean_line for x in ['ပိတ်', 'အပိတ်', 'နောက်', 'န', 'ပ']):
        nums = re.findall(r'\d', clean_line)
        total_spots += len(nums) * 10

    # 5. ဘရိတ် (၁၀ ကွက်)
    elif any(x in clean_line for x in ['ဘရိတ်', 'bk']):
        nums = re.findall(r'\d', clean_line)
        total_spots += len(nums) * 10

    # 6. ခွေ (n * n-1)
    elif ('ခွေ' in clean_line or 'ခ' in clean_line) and not any(x in clean_line for x in ['ပူး', 'အပူးပါ']):
        num_str = re.search(r'(\d+)', clean_line).group(1)
        n = len(num_str)
        total_spots += (n * (n - 1))

    # 7. ခွေပူး (n * n)
    elif any(x in clean_line for x in ['ပူး', 'အပူးပါ', 'ခွေပူး']):
        if 'ခွေ' in clean_line or 'ခ' in clean_line:
            num_str = re.search(r'(\d+)', clean_line).group(1)
            n = len(num_str)
            total_spots += (n * n)

    # 8. စုံဘရိတ် / မဘရိတ် (၅၀ ကွက်)
    if any(x in clean_line for x in ['စုံဘရိတ်', 'စုံbk', 'စဘရိတ်']): total_spots += 50
    if any(x in clean_line for x in ['မဘရိတ်', 'မbk']): total_spots += 50

    # 9. ပါဝါ / နက္ခတ် / အပူးစုံ (၁၀ ကွက်စီ)
    if any(x in clean_line for x in ['ပါဝါ', 'ပဝ', 'pw', 'power']): total_spots += 10
    if any(x in clean_line for x in ['နက္ခတ်', 'nk', 'နက', 'နခ']): total_spots += 10
    if any(x in clean_line for x in ['အပူးစုံ', 'အပူး', 'ပူး']) and 'ခွေ' not in clean_line: 
        if 'စုံပူး' in clean_line or 'မပူး' in clean_line: total_spots += 5
        else: total_spots += 10

    # 10. ညီကို (၂၀ ကွက်)
    if any(x in clean_line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): total_spots += 20
    
    # 11. ဆယ်ပြည့် (၁၀ ကွက်)
    if any(x in clean_line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']): total_spots += 10

    # 12. စုံစုံ / မမ / စုံမ / မစ (၂၅ ကွက်)
    if any(x in clean_line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
        total_spots += 25

    # 13. ကပ် / ကို (n * n)
    if 'ကပ်' in clean_line or 'ကို' in clean_line:
        parts = re.findall(r'(\d+)', clean_line)
        if len(parts) >= 2:
            total_spots += len(parts[0]) * len(parts[1])

    # ဒဲ့ဂဏန်းများ ရှာဖွေခြင်း (ဥပမာ- 12 17 62)
    digits = re.findall(r'\b\d{2}\b', clean_line)
    
    # R တွက်နည်း (Special Case: 23 45=500R250)
    if 'r' in clean_line or 'အာ' in clean_line:
        if digits:
            if 'r' in clean_line and any(char.isdigit() for char in clean_line.split('r')[-1]):
                # ဒဲ့ 500 + R 250 ပုံစံ
                r_parts = clean_line.split('r')
                main_amt = extract_amount(r_parts[0]) or line_amount
                r_amt = extract_amount(r_parts[1])
                return (len(digits) * main_amt) + (len(digits) * r_amt)
            else:
                # R ပါရင် ၂ ဆ
                total_spots += len(digits) * 2
        else:
            # Keywords တွေမှာ R ပါရင် (ဥပမာ- စမ R)
            total_spots *= 2
    else:
        total_spots += len(digits)

    return total_spots * line_amount

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    text = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    
    lines = text.strip().split('\n')
    
    # နောက်ဆုံးစာကြောင်းမှ Amount ကို အရင်းရှာ
    default_amount = 0
    for line in reversed(lines):
        amt = extract_amount(line)
        if amt:
            default_amount = amt
            break
            
    name_2d = get_2d_name(text)
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
    print("Bot is running...")
    app.run_polling()
    
