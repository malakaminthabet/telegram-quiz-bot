# 🧮 بوت اختبارات رياضيات النهايات - متوافق مع Python 3.13
import os
import asyncio
import json
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 التوكن من متغيرات البيئة
TOKEN = os.environ.get('TELEGRAM_TOKEN')

# 👨🏫 رقم المعلم - ضع رقمك هنا!
TEACHER_ID = 8422436251

# 📊 قاعدة بيانات بسيطة
class Database:
    def __init__(self):
        self.data_file = 'data.json'
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'students': {}, 'total_questions': 0, 'correct_answers': 0}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def register_student(self, user_id, name):
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
            
            self.data['total_questions'] += 1
            if is_correct:
                self.data['correct_answers'] += 1
            
            self.save_data()
            return self.data['students'][user_id]

db = Database()

# 📚 أسئلة صح/خطأ
TRUE_FALSE_QUESTIONS = [
    {"id": 1, "q": "lim┬(x→0)〖sin(x)/x = 1〗", "ans": True, "exp": "نعم، هذه نهاية أساسية"},
    {"id": 2, "q": "lim┬(x→∞)〖1/x = ∞〗", "ans": False, "exp": "خطأ، النهاية = 0"},
    {"id": 3, "q": "lim┬(x→2)〖(x²-4)/(x-2)=4〗", "ans": True, "exp": "صحيح، (x²-4)/(x-2)=x+2"},
    {"id": 4, "q": "lim┬(x→0)〖(1+x)^(1/x)=e〗", "ans": True, "exp": "نعم، تعريف العدد e"},
    {"id": 5, "q": "إذا lim┬(x→a)〖f(x)〗 موجودة، f(a) يجب أن تكون معرفة", "ans": False, "exp": "خطأ، النهاية لا تتطلب تعريف الدالة عند النقطة"}
]

# 📚 أسئلة خيارات متعددة
MCQ_QUESTIONS = [
    {"id": 1, "q": "ما قيمة: lim┬(x→3)〖(x²-9)/(x-3)〗؟", "ops": ["0", "3", "6", "9"], "ans": 2, "exp": "الحل: (x²-9)/(x-3)=x+3، النهاية=6"},
    {"id": 2, "q": "lim┬(x→0)〖(e^x-1)/x〗=؟", "ops": ["0", "1", "e", "∞"], "ans": 1, "exp": "نهاية أساسية = 1"},
    {"id": 3, "q": "lim┬(x→∞)〖(3x²+2x+1)/(x²+5)〗=؟", "ops": ["0", "1", "3", "∞"], "ans": 2, "exp": "النهاية = معامل أعلى درجة = 3"},
    {"id": 4, "q": "ما قيمة: lim┬(x→π/2)〖tan(x)〗؟", "ops": ["0", "1", "π/2", "∞"], "ans": 3, "exp": "tan(π/2) غير معرفة، النهاية = ∞"},
    {"id": 5, "q": "lim┬(x→1)〖(√x-1)/(x-1)〗=؟", "ops": ["0", "1/2", "1", "2"], "ans": 1, "exp": "بضرب في (√x+1)/(√x+1)، النهاية=1/2"},
    {"id": 6, "q": "ما قيمة: lim┬(x→0)〖(ln(1+x))/x〗؟", "ops": ["0", "1", "e", "∞"], "ans": 1, "exp": "نهاية أساسية = 1"},
    {"id": 7, "q": "lim┬(x→∞)〖(1+1/x)^x〗=؟", "ops": ["0", "1", "e", "∞"], "ans": 2, "exp": "هذا تعريف العدد e"},
    {"id": 8, "q": "ما قيمة: lim┬(x→0)〖(1-cos(x))/x²〗؟", "ops": ["0", "1/2", "1", "2"], "ans": 1, "exp": "باستخدام متطابقة مثلثية، النهاية=1/2"},
    {"id": 9, "q": "lim┬(x→2)〖|x-2|/(x-2)〗=؟", "ops": ["-1", "0", "1", "غير موجودة"], "ans": 3, "exp": "النهاية من اليمين=1، من اليسار=-1، إذن غير موجودة"},
    {"id": 10, "q": "ما قيمة: lim┬(x→0)〖(sin(3x))/x〗؟", "ops": ["0", "1", "3", "∞"], "ans": 2, "exp": "باستخدام lim sin(ax)/(ax)=1، النهاية=3"}
]

# 🎯 دوال البوت
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.register_student(user.id, user.first_name)
    
    if is_new:
        msg = f"🎉 أهلاً {user.first_name}!\nتم تسجيلك في بوت اختبارات النهايات."
    else:
        student = db.data['students'].get(str(user.id), {})
        msg = f"👋 أهلًا بعودتك {user.first_name}!\nنتيجتك: {student.get('correct', 0)}/{student.get('total', 0)}"
    
    msg += "\n\n📋 الأوامر:\n/start - البداية\n/truefalse - 5 أسئلة صح/خطأ\n/mcq - 10 أسئلة خيارات\n/score - نتيجتك\n/top - المتصدرين\n/stats - للمعلم فقط"
    
    await update.message.reply_text(msg)

async def truefalse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(TRUE_FALSE_QUESTIONS)
    
    buttons = [
        [InlineKeyboardButton("✅ صحيح", callback_data=f"tf_{q['id']}_true")],
        [InlineKeyboardButton("❌ خطأ", callback_data=f"tf_{q['id']}_false")]
    ]
    
    text = f"🔵 سؤال صح/خطأ:\n\n❓ {q['q']}"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def mcq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(MCQ_QUESTIONS)
    
    buttons = []
    letters = ['أ', 'ب', 'ج', 'د']
    for i, option in enumerate(q['ops']):
        buttons.append([InlineKeyboardButton(f"{letters[i]}. {option}", callback_data=f"mcq_{q['id']}_{i}")])
    
    text = f"🔴 سؤال خيارات:\n\n❓ {q['q']}"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    q_type = data[0]
    q_id = int(data[1])
    answer = data[2]
    
    if q_type == 'tf':
        q = next((q for q in TRUE_FALSE_QUESTIONS if q['id'] == q_id), None)
        if q:
            user_answer = (answer == 'true')
            is_correct = (user_answer == q['ans'])
            
            if is_correct:
                msg = f"✅ صحيح!\n\n📝 {q['exp']}"
            else:
                correct = "صحيح" if q['ans'] else "خطأ"
                msg = f"❌ خطأ!\nالإجابة الصحيحة: {correct}\n\n📝 {q['exp']}"
            
            db.update_score(query.from_user.id, is_correct)
    
    elif q_type == 'mcq':
        q = next((q for q in MCQ_QUESTIONS if q['id'] == q_id), None)
        if q:
            user_answer = int(answer)
            is_correct = (user_answer == q['ans'])
            letters = ['أ', 'ب', 'ج', 'د']
            
            if is_correct:
                msg = f"✅ إجابة صحيحة!\n\n📝 {q['exp']}"
            else:
                correct_letter = letters[q['ans']]
                correct_answer = q['ops'][q['ans']]
                msg = f"❌ إجابة خاطئة!\nالصحيحة: {correct_letter}. {correct_answer}\n\n📝 {q['exp']}"
            
            db.update_score(query.from_user.id, is_correct)
    
    # إضافة النتيجة الحالية
    user_id = str(query.from_user.id)
    if user_id in db.data['students']:
        student = db.data['students'][user_id]
        msg += f"\n\n📊 نتيجتك: {student['correct']}/{student['total']}"
    
    msg += "\n\n🔁 /truefalse - /mcq"
    await query.edit_message_text(msg)

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    for i, (name, perc, correct, total) in enumerate(rankings[:5]):
        medal = medals[i] if i < len(medals) else "🔸"
        text += f"{medal} {name}: {perc:.1f}% ({correct}/{total})\n"
    
    await update.message.reply_text(text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("🔒 هذا الأمر للمعلم فقط!")
        return
    
    total_students = len(db.data['students'])
    active_students = sum(1 for s in db.data['students'].values() if s['total'] > 0)
    total_questions = db.data['total_questions']
    total_correct = db.data['correct_answers']
    
    percent = (total_correct/total_questions*100) if total_questions > 0 else 0
    
    stats_text = f"""
👨🏫 إحصائيات المعلم:

👥 الطلاب المسجلين: {total_students}
🎯 الطلاب النشطين: {active_students}
📝 إجمالي الأسئلة المجابة: {total_questions}
✅ الإجابات الصحيحة: {total_correct}
📈 نسبة النجاح: {percent:.1f}%
"""
    await update.message.reply_text(stats_text)

# 🔧 الحل لمشكلة Python 3.13
def main():
    """الدالة الرئيسية المعدلة لتعمل مع Python 3.13"""
    print("=" * 50)
    print("🧮 بوت اختبارات رياضيات النهايات")
    print("=" * 50)
    print(f"📅 بدأ التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"👥 الطلاب المسجلين: {len(db.data['students'])}")
    print(f"📝 الأسئلة المجابة: {db.data['total_questions']}")
    print("✅ البوت يعمل 24/7 على Render!")
    print("=" * 50)
    print("\n📱 **تعليمات:**")
    print("1. اذهب إلى Telegram وابحث عن بوتك")
    print("2. اكتب /start للتسجيل")
    print("3. اكتب /truefalse لأسئلة صح/خطأ")
    print("4. اكتب /mcq لأسئلة خيارات متعددة")
    print("5. اكتب /score لمتابعة تقدمك")
    print("=" * 50)
    
    # حل مشكلة asyncio في Python 3.13
    import nest_asyncio
    nest_asyncio.apply()
    
    # إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("truefalse", truefalse_command))
    app.add_handler(CommandHandler("mcq", mcq_command))
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # إضافة معالجات الاستجابات
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^tf_"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^mcq_"))
    
    # تشغيل البوت بطريقة متوافقة مع Python 3.13
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(app.run_polling())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
