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
    match = re.search(r'(\d+)\s*$', line.strip())
    return int(match.group(1)) if match else None

def calculate_line_logic(line, default_amount):
    # သင်္ကေတများ ရှင်းလင်းခြင်း
    clean_line = line.replace('-', ' ').replace('=', ' ').replace('*', ' ').replace('/', ' ').lower()
    
    line_amount = extract_amount(line) or default_amount
    if not line_amount: return 0

    total_spots = 0

    # Keyword ရဲ့ ရှေ့မှာကပ်နေတဲ့ ဂဏန်းတွေကိုပဲ ယူတဲ့ Function
    def get_target_nums(l, keyword):
        # Keyword ရဲ့ ရှေ့အပိုင်းကို ဖြတ်ယူတယ်
        before_kw = l.split(keyword)[0].strip()
        # အဲဒီအပိုင်းထဲက နောက်ဆုံးတွေ့တဲ့ ဂဏန်းစုကို ယူတယ် (ဥပမာ "abc 567top" ဆိုရင် "567" ကိုယူမယ်)
        match = re.search(r'(\d+)$', before_kw)
        if match:
            return list(match.group(1))
        return []

    # 1. ပတ်ပူး / ၂၀ကွက်
    pb_kws = ['ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']
    found_special = False
    for kw in pb_kws:
        if kw in clean_line:
            nums = get_target_nums(clean_line, kw)
            total_spots += len(nums) * 20
            found_special = True
            break
            
    # 2. ပတ်သီး / အပါ (၁၉ ကွက်)
    if not found_special:
        p_kws = ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']
        for kw in p_kws:
            if kw in clean_line:
                nums = get_target_nums(clean_line, kw)
                total_spots += len(nums) * 19
                found_special = True
                break

    # 3. ထိပ်စီး (၁၀ ကွက်)
    t_kws = ['ထိပ်', 'top', 't']
    for kw in t_kws:
        if kw in clean_line and not found_special:
            nums = get_target_nums(clean_line, kw)
            total_spots += len(nums) * 10
            found_special = True
            break

    # 4. အပိတ် / နောက် (၁၀ ကွက်)
    n_kws = ['ပိတ်', 'အပိတ်', 'နောက်', 'န', 'ပ']
    for kw in n_kws:
        if kw in clean_line and not found_special:
            nums = get_target_nums(clean_line, kw)
            total_spots += len(nums) * 10
            found_special = True
            break

    # 5. ဘရိတ် (၁၀ ကွက်)
    bk_kws = ['ဘရိတ်', 'bk']
    for kw in bk_kws:
        if kw in clean_line and not found_special:
            nums = get_target_nums(clean_line, kw)
            total_spots += len(nums) * 10
            found_special = True
            break

    # 6. ခွေ (n * n-1) နှင့် ခွေပူး (n * n)
    if 'ခွေ' in clean_line or 'ခ' in clean_line:
        match = re.search(r'(\d+)', clean_line)
        if match:
            n = len(match.group(1))
            if any(x in clean_line for x in ['ပူး', 'အပူးပါ', 'အပြီးပါ']):
                total_spots += (n * n)
            else:
                total_spots += (n * (n - 1))
        found_special = True

    # 7. အထူး Keywords များ (ပါဝါ၊ နက္ခတ်၊ စုံမ စသည်)
    if any(x in clean_line for x in ['စုံဘရိတ်', 'စုံbk', 'စဘရိတ်', 'မဘရိတ်', 'မbk']): total_spots += 50
    if any(x in clean_line for x in ['ပါဝါ', 'ပဝ', 'pw', 'power']): total_spots += 10
    if any(x in clean_line for x in ['နက္ခတ်', 'nk', 'နက', 'နခ']): total_spots += 10
    if any(x in clean_line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): total_spots += 20
    if any(x in clean_line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']): total_spots += 10
    if any(x in clean_line for x in ['အပူးစုံ', 'အပူး', 'ပူး']) and 'ခွေ' not in clean_line:
        if 'စုံပူး' in clean_line or 'မပူး' in clean_line: total_spots += 5
        else: total_spots += 10
    if any(x in clean_line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']): total_spots += 25

    # 8. ကပ် / ကို
    if 'ကပ်' in clean_line or 'ကို' in clean_line:
        parts = re.findall(r'(\d+)', clean_line)
        if len(parts) >= 2:
            total_spots += len(parts[0]) * len(parts[1])

    # 9. ဒဲ့ဂဏန်းများ (၂ လုံးတွဲ သီးသန့်)
    # Keyword တွေထဲက ဂဏန်းတွေနဲ့ မရောအောင် သန့်စင်ပြီးမှ ရှာမယ်
    temp_text = clean_line
    all_kws = pb_kws + p_kws + t_kws + n_kws + bk_kws + ['ခွေ', 'ခ']
    for k in all_kws: temp_text = temp_text.replace(k, ' keyword ')
    
    digits = re.findall(r'\b\d{2}\b', temp_text)
    
    # R တွက်နည်း (ဒဲ့ + R ခွဲတွက်တာအပါအဝင်)
    if 'r' in clean_line or 'အာ' in clean_line:
        if digits:
            if 'r' in clean_line and any(c.isdigit() for c in clean_line.split('r')[-1]):
                r_parts = clean_line.split('r')
                main_amt = extract_amount(r_parts[0]) or line_amount
                r_amt = extract_amount(r_parts[1])
                return (len(digits) * main_amt) + (len(digits) * r_amt)
            else:
                total_spots += len(digits) * 2
        else:
            total_spots *= 2 # Keyword တွေအတွက် R ပါရင် ၂ ဆ
    else:
        total_spots += len(digits)

    return total_spots * line_amount

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    lines = text.strip().split('\n')
    
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
        response = f"👤 {username}\n--------------------\n{name_2d} စုစုပေါင်း = {grand_total:,} ကျပ်\nကံကောင်းပါစေရှင့်"
        await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
