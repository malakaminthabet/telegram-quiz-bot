# 🧮 بوت اختبارات رياضيات النهايات
# 📚 صح/خطأ + خيارات متعددة
# 👨🏫 إعداد: معلم الرياضيات

import os
import asyncio
import json
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 التوكن - سأضيفه في Render
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8541804759:AAEb2NnuZoCxDalpgdsGUgaoEcwctj7DYaw')
TEACHER_ID = 8422436251  # غير هذا الرقم!

class Database:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open('data.json', 'r') as f:
                return json.load(f)
        except:
            return {'students': {}, 'total': 0, 'correct': 0}
    
    def save_data(self):
        with open('data.json', 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def register(self, user_id, name):
        if str(user_id) not in self.data['students']:
            self.data['students'][str(user_id)] = {
                'name': name, 'correct': 0, 'total': 0,
                'joined': datetime.now().strftime('%Y-%m-%d')
            }
            self.save_data()
            return True
        return False
    
    def update_score(self, user_id, is_correct):
        user = self.data['students'].get(str(user_id))
        if user:
            user['total'] += 1
            if is_correct:
                user['correct'] += 1
                self.data['correct'] += 1
            self.data['total'] += 1
            self.save_data()
            return user

db = Database()

# 🎯 أسئلة صح/خطأ (5 أسئلة)
TF_QUESTIONS = [
    {"id": 1, "q": "lim┬(x→0)〖sin(x)/x = 1〗", "ans": True, "exp": "نعم، نهاية أساسية"},
    {"id": 2, "q": "lim┬(x→∞)〖1/x = ∞〗", "ans": False, "exp": "خطأ، النهاية = 0"},
    {"id": 3, "q": "lim┬(x→2)〖(x²-4)/(x-2)=4〗", "ans": True, "exp": "صحيح، (x²-4)/(x-2)=x+2"},
    {"id": 4, "q": "lim┬(x→0)〖(1+x)^(1/x)=e〗", "ans": True, "exp": "نعم، تعريف العدد e"},
    {"id": 5, "q": "إذا lim┬(x→a)〖f(x)〗 موجودة، f(a) يجب أن تكون معرفة", "ans": False, "exp": "خطأ، النهاية لا تتطلب تعريف الدالة عند النقطة"}
]

# 🎯 أسئلة خيارات (10 أسئلة)
MCQ_QUESTIONS = [
    {"id": 1, "q": "ما قيمة: lim┬(x→3)〖(x²-9)/(x-3)〗؟", "ops": ["0","3","6","9"], "ans": 2, "exp": "الحل: (x²-9)/(x-3)=x+3 ← النهاية=6"},
    {"id": 2, "q": "lim┬(x→0)〖(e^x-1)/x〗=؟", "ops": ["0","1","e","∞"], "ans": 1, "exp": "نهاية أساسية = 1"},
    {"id": 3, "q": "lim┬(x→∞)〖(3x²+2x+1)/(x²+5)〗=؟", "ops": ["0","1","3","∞"], "ans": 2, "exp": "النهاية = معامل أعلى درجة = 3"},
    {"id": 4, "q": "ما قيمة: lim┬(x→π/2)〖tan(x)〗؟", "ops": ["0","1","π/2","∞"], "ans": 3, "exp": "tan(π/2) غير معرفة ← النهاية = ∞"},
    {"id": 5, "q": "lim┬(x→1)〖(√x-1)/(x-1)〗=؟", "ops": ["0","1/2","1","2"], "ans": 1, "exp": "بضرب في (√x+1)/(√x+1) ← النهاية=1/2"},
    {"id": 6, "q": "ما قيمة: lim┬(x→0)〖(ln(1+x))/x〗؟", "ops": ["0","1","e","∞"], "ans": 1, "exp": "نهاية أساسية = 1"},
    {"id": 7, "q": "lim┬(x→∞)〖(1+1/x)^x〗=؟", "ops": ["0","1","e","∞"], "ans": 2, "exp": "هذا تعريف العدد e"},
    {"id": 8, "q": "ما قيمة: lim┬(x→0)〖(1-cos(x))/x²〗؟", "ops": ["0","1/2","1","2"], "ans": 1, "exp": "باستخدام متطابقة مثلثية ← النهاية=1/2"},
    {"id": 9, "q": "lim┬(x→2)〖|x-2|/(x-2)〗=؟", "ops": ["-1","0","1","غير موجودة"], "ans": 3, "exp": "النهاية من اليمين=1، من اليسار=-1 ← غير موجودة"},
    {"id": 10, "q": "ما قيمة: lim┬(x→0)〖(sin(3x))/x〗؟", "ops": ["0","1","3","∞"], "ans": 2, "exp": "باستخدام lim sin(ax)/(ax)=1 ← النهاية=3"}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.register(user.id, user.first_name)
    
    msg = f"{'🎉 أهلاً' if is_new else '👋 أهلًا بعودتك'} {user.first_name}!\n"
    msg += "أنا بوت اختبارات رياضيات النهايات.\n\n"
    msg += "📋 الأوامر:\n/start - البداية\n/truefalse - 5 أسئلة صح/خطأ\n/mcq - 10 أسئلة خيارات\n/score - نتيجتك\n/top - المتصدرين"
    
    await update.message.reply_text(msg)

async def truefalse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(TF_QUESTIONS)
    buttons = [
        [InlineKeyboardButton("✅ صحيح", callback_data=f"tf_{q['id']}_true")],
        [InlineKeyboardButton("❌ خطأ", callback_data=f"tf_{q['id']}_false")]
    ]
    await update.message.reply_text(f"❓ {q['q']}", reply_markup=InlineKeyboardMarkup(buttons))

async def mcq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(MCQ_QUESTIONS)
    buttons = []
    letters = ['أ', 'ب', 'ج', 'د']
    for i, opt in enumerate(q['ops']):
        buttons.append([InlineKeyboardButton(f"{letters[i]}. {opt}", callback_data=f"mcq_{q['id']}_{i}")])
    await update.message.reply_text(f"❓ {q['q']}", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    q_type, q_id, ans = data[0], int(data[1]), data[2]
    
    if q_type == 'tf':
        q = next((q for q in TF_QUESTIONS if q['id'] == q_id), None)
        if q:
            is_correct = ((ans == 'true') == q['ans'])
            msg = f"✅ صحيح!\n\n{q['exp']}" if is_correct else f"❌ خطأ!\n\n{q['exp']}"
    
    elif q_type == 'mcq':
        q = next((q for q in MCQ_QUESTIONS if q['id'] == q_id), None)
        if q:
            is_correct = (int(ans) == q['ans'])
            letters = ['أ', 'ب', 'ج', 'د']
            if is_correct:
                msg = f"✅ إجابة صحيحة!\n\n{q['exp']}"
            else:
                correct = letters[q['ans']]
                msg = f"❌ إجابة خاطئة!\nالصحيحة: {correct}\n\n{q['exp']}"
    
    # تحديث النتيجة
    if 'is_correct' in locals():
        db.update_score(query.from_user.id, is_correct)
        user = db.data['students'].get(str(query.from_user.id), {})
        msg += f"\n\n📊 نتيجتك: {user.get('correct',0)}/{user.get('total',0)}"
    
    msg += "\n\n🔁 /truefalse أو /mcq لسؤال جديد"
    await query.edit_message_text(msg)

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.data['students'].get(str(update.effective_user.id))
    if not user:
        await update.message.reply_text("⚠️ اكتب /start أولاً")
        return
    
    total, correct = user['total'], user['correct']
    percent = (correct/total*100) if total > 0 else 0
    
    report = f"📊 نتيجتك:\n✅ {correct} صحيح\n❌ {total-correct} خطأ\n🎯 {percent:.1f}%\n📅 {user['joined']}"
    await update.message.reply_text(report)

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.data['students']:
        await update.message.reply_text("🏆 لا توجد نتائج!")
        return
    
    rankings = []
    for uid, stu in db.data['students'].items():
        if stu['total'] > 0:
            percent = (stu['correct']/stu['total']*100)
            rankings.append((stu['name'], percent, stu['correct'], stu['total']))
    
    if not rankings:
        await update.message.reply_text("🏆 لم يجب أحد بعد!")
        return
    
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    text = "🏆 المتصدرون:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, perc, cor, tot) in enumerate(rankings[:5]):
        medal = medals[i] if i < len(medals) else "🎖️"
        text += f"{medal} {name}: {perc:.1f}% ({cor}/{tot})\n"
    
    await update.message.reply_text(text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("🔒 للمعلم فقط!")
        return
    
    total_stu = len(db.data['students'])
    active = sum(1 for s in db.data['students'].values() if s['total'] > 0)
    total_q = db.data['total']
    total_cor = db.data['correct']
    percent = (total_cor/total_q*100) if total_q > 0 else 0
    
    stats_text = f"""👨🏫 إحصائيات:
👥 الطلاب: {total_stu}
🎯 النشطين: {active}
📝 الأسئلة: {total_q}
✅ الصحيحة: {total_cor}
📈 النسبة: {percent:.1f}%"""
    
    await update.message.reply_text(stats_text)

async def main():
    print("🧮 بوت اختبارات النهايات يعمل...")
    print("📱 اذهب لـ Telegram وابحث عن بوتك")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("truefalse", truefalse))
    app.add_handler(CommandHandler("mcq", mcq))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(handle_answer))
    
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
