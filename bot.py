import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = "8543212797:AAFMPikuXIga7d3YvpL8avOA8XkTk0C4S0o"

def calculate_line_logic(line, default_amount):
    line = line.lower().strip()
    if not line or '%' in line: return 0

    # 1. Amount ကို အရင်ဆုံး ရှာဖွေခြင်း
    # စာကြောင်းအဆုံးမှ ဂဏန်းကို amount အဖြစ် ယူသည်
    match_amount = re.search(r'(\d+)\s*$', line)
    amount = int(match_amount.group(1)) if match_amount else default_amount
    if not amount: return 0

    # Amount ကို ဖယ်ထုတ်ပြီး ကျန်တဲ့ စာသား (Pure Logic) ကိုပဲ စစ်ဆေးမည်
    clean_line = re.sub(r'\d+\s*$', '', line).strip()
    is_r = any(x in clean_line for x in ['r', 'အာ'])
    
    total_spots = 0

    # --- [Logic များ စစ်ဆေးခြင်း] ---

    # (A) ခွေ / ခွေပူး (ဥပမာ- 123ခွေ၊ 123ခွေပူး)
    if 'ခွေ' in clean_line or 'ခ' in clean_line:
        nums = re.search(r'(\d+)', clean_line)
        if nums:
            n = len(nums.group(1))
            if any(x in clean_line for x in ['ပူး', 'အပူးပါ', 'အပြီးပါ']):
                return (n * n) * amount
            else:
                return (n * (n - 1)) * amount

    # (B) ကပ် / ကို (ဥပမာ- 12ကို34ကပ်)
    if any(x in clean_line for x in ['ကပ်', 'ကို']):
        parts = re.findall(r'(\d+)', clean_line)
        if len(parts) >= 2:
            base = len(parts[0]) * len(parts[1])
            return base * (2 if is_r else 1) * amount

    # (C) ပတ်သီး / ပတ်ပူး / ထိပ်နောက်
    digits = re.findall(r'\b\d\b', clean_line) # ဂဏန်းတစ်လုံးချင်းစီ
    if any(x in clean_line for x in ['ပတ်ပူး', 'ပူးပို', 'ထိပ်နောက်', 'ထန']):
        return len(digits) * 20 * amount
    if any(x in clean_line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
        return len(digits) * 19 * amount

    # (D) ထိပ်စီး / အပိတ် / ဘရိတ်
    if any(x in clean_line for x in ['ထိပ်', 'top', 't']):
        return (len(digits) if digits else 1) * 10 * amount
    if any(x in clean_line for x in ['ပိတ်', 'အပိတ်', 'နောက်', 'န']):
        return (len(digits) if digits else 1) * 10 * amount
    if any(x in clean_line for x in ['ဘရိတ်', 'bk']):
        return (len(digits) if digits else 1) * 10 * amount

    # (E) စုံ/မ နှင့် အထူး Keywords (ပါဝါ၊ ညီကို၊ နက္ခတ်၊ စုံဘရိတ်)
    temp_spots = 0
    if any(x in clean_line for x in ['ပါဝါ', 'pw', 'power']): temp_spots += 10
    if any(x in clean_line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): temp_spots += 20
    if any(x in clean_line for x in ['နက္ခတ်', 'nk', 'နက', 'နခ']): temp_spots += 10
    if any(x in clean_line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်']): temp_spots += 10
    if any(x in clean_line for x in ['အပူးစုံ', 'အပူး', 'ပူး']): temp_spots += 10
    if any(x in clean_line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်']): temp_spots += 50
    if any(x in clean_line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']): temp_spots += (50 if is_r else 25)

    if temp_spots > 0:
        return temp_spots * amount

    # (F) ဒဲ့ဂဏန်းများ (ဥပမာ- 12 34 56)
    # စာကြောင်းထဲက ၂ လုံးတွဲဂဏန်းအားလုံးကို ရှာသည်
    two_digits = re.findall(r'(\d{2})', clean_line)
    if two_digits:
        # 500r250 logic
        if 'r' in line:
            r_match = re.search(r'r(\d+)$', line)
            if r_match:
                r_amt = int(r_match.group(1))
                return (len(two_digits) * amount) + (len(two_digits) * r_amt)
            return (len(two_digits) * 2) * amount
        return len(two_digits) * amount

    return 0

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    username = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name

    lines = text.strip().split('\n')
    
    # ၁။ Default Amount နှင့် % ရှာဖွေခြင်း
    default_amount = 0
    comm_percent = 0
    for line in lines:
        if '%' in line:
            p_match = re.search(r'(\d+)\s*%', line)
            if p_match: comm_percent = int(p_match[1])
        
        # စာကြောင်းတစ်ကြောင်းချင်းစီရဲ့ အဆုံးမှာပါတဲ့ amount ကို default အဖြစ် မှတ်သားမယ်
        amt_match = re.search(r'(\d+)\s*$', line.strip())
        if amt_match:
            default_amount = int(amt_match.group(1))

    # ၂။ စုစုပေါင်းတွက်ချက်ခြင်း
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
        response += "🍀 ကံကောင်းပါစေရှင့်"
        await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Shwethoon Bot is running...")
    app.run_polling()
