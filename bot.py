# 🧮 بوت اختبارات رياضيات النهايات (Limits)
# 👨🏫 إعداد: معلم الرياضيات

import os
import asyncio
import json
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 التوكن من متغيرات البيئة (سأضيفه في Render لاحقاً)
TOKEN = os.environ.get('TELEGRAM_TOKEN', 'ضع_توكن_بوتك_هنا')

# 👨🏫 رقم المعلم (غير هذا الرقم!)
TEACHER_ID = 123456789

# 📊 قاعدة البيانات البسيطة
class Database:
    def __init__(self):
        self.data_file = 'data.json'
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'students': {}, 'questions': 0, 'correct': 0}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def register(self, user_id, name):
        user_id = str(user_id)
        if user_id not in self.data['students']:
            self.data['students'][user_id] = {
                'name': name,
                'correct': 0,
                'total': 0,
                'joined': datetime.now().strftime('%Y-%m-%d')
            }
            self.save_data()
            return True
        return False
    
    def update_score(self, user_id, is_correct):
        user_id = str(user_id)
        if user_id in self.data['students']:
            self.data['students'][user_id]['total'] += 1
            if is_correct:
                self.data['students'][user_id]['correct'] += 1
            
            self.data['questions'] += 1
            if is_correct:
                self.data['correct'] += 1
            
            self.save_data()
            return self.data['students'][user_id]

db = Database()

# 📚 أسئلة صح/خطأ في النهايات (5 أسئلة)
TRUE_FALSE = [
    {
        "id": 1,
        "question": "lim┬(x→0)〖sin(x)/x = 1〗",
        "answer": True,
        "explain": "نعم، هذه نهاية أساسية معروفة"
    },
    {
        "id": 2,
        "question": "lim┬(x→∞)〖1/x = ∞〗",
        "answer": False,
        "explain": "خطأ، النهاية = 0"
    },
    {
        "id": 3,
        "question": "lim┬(x→2)〖(x² - 4)/(x - 2) = 4〗",
        "answer": True,
        "explain": "صحيح، (x²-4)/(x-2) = x+2 عندما x≠2"
    },
    {
        "id": 4,
        "question": "lim┬(x→0)〖(1 + x)^(1/x) = e〗",
        "answer": True,
        "explain": "نعم، هذه صيغة العدد النيبيري e"
    },
    {
        "id": 5,
        "question": "إذا lim┬(x→a)〖f(x)〗 موجودة، فإن f(a) يجب أن تكون معرفة",
        "answer": False,
        "explain": "خطأ، النهاية لا تتطلب تعريف الدالة عند النقطة"
    }
]

# 📚 أسئلة خيارات متعددة في النهايات (10 أسئلة)
MCQS = [
    {
        "id": 1,
        "question": "ما قيمة: lim┬(x→3)〖(x² - 9)/(x - 3)〗؟",
        "options": ["0", "3", "6", "9"],
        "answer": 2,
        "explain": "الحل: (x²-9)/(x-3) = x+3، النهاية = 6"
    },
    {
        "id": 2,
        "question": "lim┬(x→0)〖(e^x - 1)/x〗 = ?",
        "options": ["0", "1", "e", "∞"],
        "answer": 1,
        "explain": "هذه نهاية أساسية = 1"
    },
    {
        "id": 3,
        "question": "lim┬(x→∞)〖(3x² + 2x + 1)/(x² + 5)〗 = ?",
        "options": ["0", "1", "3", "∞"],
        "answer": 2,
        "explain": "النهاية = معامل أعلى درجة = 3/1 = 3"
    },
    {
        "id": 4,
        "question": "ما قيمة: lim┬(x→π/2)〖tan(x)〗؟",
        "options": ["0", "1", "π/2", "∞"],
        "answer": 3,
        "explain": "tan(π/2) غير معرفة، النهاية = ∞"
    },
    {
        "id": 5,
        "question": "lim┬(x→1)〖(√x - 1)/(x - 1)〗 = ?",
        "options": ["0", "1/2", "1", "2"],
        "answer": 1,
        "explain": "بضرب في (√x+1)/(√x+1)، النهاية = 1/2"
    },
    {
        "id": 6,
        "question": "ما قيمة: lim┬(x→0)〖(ln(1 + x))/x〗؟",
        "options": ["0", "1", "e", "∞"],
        "answer": 1,
        "explain": "نهاية أساسية = 1"
    },
    {
        "id": 7,
        "question": "lim┬(x→∞)〖(1 + 1/x)^x〗 = ?",
        "options": ["0", "1", "e", "∞"],
        "answer": 2,
        "explain": "هذا تعريف العدد e"
    },
    {
        "id": 8,
        "question": "ما قيمة: lim┬(x→0)〖(1 - cos(x))/x²〗؟",
        "options": ["0", "1/2", "1", "2"],
        "answer": 1,
        "explain": "باستخدام متطابقة مثلثية، النهاية = 1/2"
    },
    {
        "id": 9,
        "question": "lim┬(x→2)〖|x - 2|/(x - 2)〗 = ?",
        "options": ["-1", "0", "1", "غير موجودة"],
        "answer": 3,
        "explain": "النهاية من اليمين = 1، من اليسار = -1، إذن غير موجودة"
    },
    {
        "id": 10,
        "question": "ما قيمة: lim┬(x→0)〖(sin(3x))/x〗؟",
        "options": ["0", "1", "3", "∞"],
        "answer": 2,
        "explain": "باستخدام lim sin(ax)/(ax)=1، النهاية = 3"
    }
]

# ==================== دوال البوت ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.register(user.id, user.first_name)
    
    if is_new:
        msg = f"🎉 أهلاً {user.first_name}!\nتم تسجيلك في بوت اختبارات النهايات."
    else:
        student = db.data['students'].get(str(user.id), {})
        msg = f"👋 أهلًا بعودتك {user.first_name}!\nنتيجتك: {student.get('correct', 0)}/{student.get('total', 0)}"
    
    msg += """
    
📋 الأوامر:
/start - البداية
/help - المساعدة
/truefalse - 5 أسئلة صح/خطأ
/mcq - 10 أسئلة خيارات متعددة
/score - نتيجتك
/top - المتصدرين
/stats - للمعلم فقط
"""
    await update.message.reply_text(msg)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🧮 بوت اختبارات رياضيات النهايات

🎯 أنواع الأسئلة:
1. صح/خطأ - 5 أسئلة (/truefalse)
2. خيارات متعددة - 10 أسئلة (/mcq)

📚 مواضيع الأسئلة:
• النهايات الأساسية
• النهايات عند اللانهاية
• النهايات المثلثية
• النهايات الأسية

🚀 ابدأ الآن بـ:
/truefalse أو /mcq
"""
    await update.message.reply_text(help_text)

async def truefalse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(TRUE_FALSE)
    
    buttons = [
        [InlineKeyboardButton("✅ صحيح", callback_data=f"tf_{q['id']}_true")],
        [InlineKeyboardButton("❌ خطأ", callback_data=f"tf_{q['id']}_false")]
    ]
    
    text = f"🔵 سؤال صح/خطأ:\n\n❓ {q['question']}"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def mcq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(MCQS)
    
    buttons = []
    letters = ['أ', 'ب', 'ج', 'د']
    for i, option in enumerate(q['options']):
        buttons.append([InlineKeyboardButton(f"{letters[i]}. {option}", callback_data=f"mcq_{q['id']}_{i}")])
    
    text = f"🔴 سؤال خيارات:\n\n❓ {q['question']}"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    q_type = data[0]
    q_id = int(data[1])
    answer = data[2]
    
    if q_type == 'tf':
        q = next((q for q in TRUE_FALSE if q['id'] == q_id), None)
        if q:
            user_answer = (answer == 'true')
            is_correct = (user_answer == q['answer'])
            
            if is_correct:
                msg = f"✅ صحيح!\n\n📝 {q['explain']}"
            else:
                correct = "صحيح" if q['answer'] else "خطأ"
                msg = f"❌ خطأ!\nالإجابة الصحيحة: {correct}\n\n📝 {q['explain']}"
            
            db.update_score(query.from_user.id, is_correct)
    
    elif q_type == 'mcq':
        q = next((q for q in MCQS if q['id'] == q_id), None)
        if q:
            user_answer = int(answer)
            is_correct = (user_answer == q['answer'])
            letters = ['أ', 'ب', 'ج', 'د']
            
            if is_correct:
                msg = f"✅ إجابة صحيحة!\n\n📝 {q['explain']}"
            else:
                correct_letter = letters[q['answer']]
                correct_answer = q['options'][q['answer']]
                msg = f"❌ إجابة خاطئة!\nالصحيحة: {correct_letter}. {correct_answer}\n\n📝 {q['explain']}"
            
            db.update_score(query.from_user.id, is_correct)
    
    # إضافة النتيجة الحالية
    user_id = str(query.from_user.id)
    if user_id in db.data['students']:
        student = db.data['students'][user_id]
        msg += f"\n\n📊 نتيجتك: {student['correct']}/{student['total']}"
    
    msg += "\n\n🔁 /truefalse - /mcq"
    await query.edit_message_text(msg)

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_id not in db.data['students']:
        await update.message.reply_text("⚠️ اكتب /start أولاً")
        return
    
    student = db.data['students'][user_id]
    total = student['total']
    correct = student['correct']
    percent = (correct/total*100) if total > 0 else 0
    
    report = f"""
📊 تقرير أدائك:

✅ الإجابات الصحيحة: {correct}
❌ الإجابات الخاطئة: {total - correct}
📝 إجمالي الأسئلة: {total}
🎯 النسبة: {percent:.1f}%

📅 انضممت: {student['joined']}
"""
    
    if percent >= 80:
        report += "\n🏆 ممتاز! مستواك رائع"
    elif percent >= 60:
        report += "\n⭐ جيد جداً! واصل التقدم"
    elif percent >= 40:
        report += "\n💪 مستوى مقبول، تدرب أكثر"
    else:
        report += "\n📚 راجع الأساسيات وتدرب"
    
    await update.message.reply_text(report)

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.data['students']:
        await update.message.reply_text("🏆 لا توجد نتائج بعد!")
        return
    
    rankings = []
    for user_id, student in db.data['students'].items():
        if student['total'] >= 3:
            percent = (student['correct']/student['total']*100)
            rankings.append((student['name'], percent, student['correct'], student['total']))
    
    if not rankings:
        await update.message.reply_text("🏆 لم يكمل أحد 3 أسئلة بعد!")
        return
    
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    text = "🏆 المتصدرون:\n\n"
    medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️"]
    
    for i, (name, percent, correct, total) in enumerate(rankings[:5]):
        medal = medals[i] if i < len(medals) else "🔸"
        text += f"{medal} {name}: {percent:.1f}% ({correct}/{total})\n"
    
    await update.message.reply_text(text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("🔒 للمعلم فقط!")
        return
    
    total_students = len(db.data['students'])
    active = sum(1 for s in db.data['students'].values() if s['total'] > 0)
    total_q = db.data['questions']
    total_correct = db.data['correct']
    percent = (total_correct/total_q*100) if total_q > 0 else 0
    
    stats_text = f"""
👨🏫 إحصائيات المعلم:

👥 الطلاب: {total_students}
🎯 النشطين: {active}
📝 الأسئلة: {total_q}
✅ الصحيحة: {total_correct}
📈 النسبة: {percent:.1f}%
"""
    await update.message.reply_text(stats_text)

async def main():
    print("🧮 بوت اختبارات النهايات يعمل...")
    print("📱 اذهب إلى Telegram وابحث عن بوتك")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("truefalse", truefalse))
    app.add_handler(CommandHandler("mcq", mcq))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(handle_answer))
    
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
  Add bot.py
