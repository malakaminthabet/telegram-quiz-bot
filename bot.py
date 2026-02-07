# 🧮 بوت اختبارات رياضيات النهايات - نسخة مستقرة
# 🔧 بدون مشاكل Conflict - يعمل 24/7 على Render
# 🎨 واجهة عربية جميلة وسهلة للمعلم

import os
import asyncio
import json
import random
import threading
import time
import requests
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import Conflict

# 🔐 التوكن من متغيرات البيئة
TOKEN = os.environ.get('TELEGRAM_TOKEN')
TEACHER_ID = 8422436251  # ❗ غيّر هذا الرقم إلى ID حسابك!

# 🌐 Flask لإبقاء البوت نشطاً
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>بوت الرياضيات التفاعلي</title>
            <meta charset="UTF-8">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 40px; 
                    border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    color: #333;
                }
                h1 { 
                    color: #2c3e50; 
                    font-size: 2.5em; 
                    margin-bottom: 20px;
                }
                .emoji { font-size: 3em; margin: 20px; }
                .status { 
                    color: #27ae60; 
                    font-size: 24px; 
                    font-weight: bold;
                    padding: 15px;
                    background: #e8f5e9;
                    border-radius: 10px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">🧮🤖</div>
                <h1>بوت اختبارات الرياضيات التفاعلي</h1>
                <div class="status">✅ البوت يعمل بنجاح!</div>
                <p>⏰ يعمل 24/7 على Render</p>
                <p>👨🏫 للمعلم: استخدم /add_question لإضافة أسئلة</p>
                <p>📱 للطلاب: ابحث عن @mathimatical_testBot</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "active", "timestamp": datetime.now().isoformat()}

@app.route('/ping')
def ping():
    return "pong"

# 📊 قاعدة البيانات
class Database:
    def __init__(self):
        self.data_file = 'data.json'
        self.questions_file = 'questions.json'
        self.data = self.load_data()
        self.questions = self.load_questions()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'students': {}, 'total_questions': 0, 'correct_answers': 0}
    
    def load_questions(self):
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            default_questions = {
                'true_false': [
                    {"id": 1, "q": "lim┬(x→0)〖sin(x)/x = 1〗", "ans": True, "exp": "نعم، هذه نهاية أساسية"},
                    {"id": 2, "q": "lim┬(x→∞)〖1/x = ∞〗", "ans": False, "exp": "خطأ، النهاية = 0"},
                    {"id": 3, "q": "lim┬(x→2)〖(x²-4)/(x-2)=4〗", "ans": True, "exp": "صحيح، (x²-4)/(x-2)=x+2"},
                ],
                'mcq': [
                    {"id": 1, "q": "ما قيمة: lim┬(x→3)〖(x²-9)/(x-3)〗؟", "ops": ["0", "3", "6", "9"], "ans": 2, "exp": "الحل: (x²-9)/(x-3)=x+3، النهاية=6"},
                    {"id": 2, "q": "lim┬(x→0)〖(e^x-1)/x〗=؟", "ops": ["0", "1", "e", "∞"], "ans": 1, "exp": "نهاية أساسية = 1"},
                ]
            }
            self.save_questions(default_questions)
            return default_questions
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def save_questions(self, questions=None):
        if questions is None:
            questions = self.questions
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    
    def register_student(self, user_id, name):
        user_id = str(user_id)
        if user_id not in self.data['students']:
            self.data['students'][user_id] = {
                'name': name,
                'correct': 0,
                'total': 0,
                'joined': datetime.now().strftime('%Y-%m-%d'),
                'last_active': datetime.now().isoformat(),
                'level': 1
            }
            self.save_data()
            return True
        return False
    
    def update_score(self, user_id, is_correct):
        user_id = str(user_id)
        if user_id in self.data['students']:
            self.data['students'][user_id]['total'] += 1
            self.data['students'][user_id]['last_active'] = datetime.now().isoformat()
            
            if is_correct:
                self.data['students'][user_id]['correct'] += 1
            
            self.data['total_questions'] += 1
            if is_correct:
                self.data['correct_answers'] += 1
            
            self.save_data()
            return self.data['students'][user_id]
    
    def add_true_false_question(self, question, answer, explanation):
        new_id = max([q['id'] for q in self.questions['true_false']], default=0) + 1
        self.questions['true_false'].append({
            "id": new_id,
            "q": question,
            "ans": answer,
            "exp": explanation
        })
        self.save_questions()
        return new_id
    
    def add_mcq_question(self, question, options, answer, explanation):
        new_id = max([q['id'] for q in self.questions['mcq']], default=0) + 1
        self.questions['mcq'].append({
            "id": new_id,
            "q": question,
            "ops": options,
            "ans": answer,
            "exp": explanation
        })
        self.save_questions()
        return new_id

db = Database()

# 🎯 دوال البوت الأساسية
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.register_student(user.id, user.first_name)
    
    welcome = f"""
✨ **مرحباً {user.first_name}!** ✨

🎯 **بوت اختبارات النهايات في الرياضيات**
📚 اختبر مهاراتك في حساب النهايات
⚡ احصل على تقييم فوري
    """
    
    if is_new:
        welcome += "\n🎉 **تم تسجيلك بنجاح!**"
    else:
        student = db.data['students'].get(str(user.id), {})
        correct = student.get('correct', 0)
        total = student.get('total', 0)
        welcome += f"\n📊 **نتيجتك:** {correct}/{total}"
    
    welcome += "\n\n🔧 **الأوامر المتاحة:**"
    welcome += "\n▫️ /truefalse - أسئلة صح/خطأ"
    welcome += "\n▫️ /mcq - أسئلة اختيار من متعدد"
    welcome += "\n▫️ /score - عرض نتيجتك"
    
    if user.id == TEACHER_ID:
        welcome += "\n\n👨🏫 **أوامر المعلم:**"
        welcome += "\n▫️ /add_question - إضافة سؤال جديد"
        welcome += "\n▫️ /view_questions - عرض الأسئلة"
    
    await update.message.reply_text(welcome)

async def truefalse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.questions['true_false']:
        await update.message.reply_text("⚠️ لا توجد أسئلة صح/خطأ متاحة حالياً.")
        return
    
    q = random.choice(db.questions['true_false'])
    buttons = [
        [InlineKeyboardButton("✅ صحيح", callback_data=f"tf_{q['id']}_true")],
        [InlineKeyboardButton("❌ خطأ", callback_data=f"tf_{q['id']}_false")]
    ]
    
    text = f"""
🔵 **سؤال صح/خطأ**

📝 {q['q']}
    """
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def mcq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.questions['mcq']:
        await update.message.reply_text("⚠️ لا توجد أسئلة اختيار من متعدد متاحة حالياً.")
        return
    
    q = random.choice(db.questions['mcq'])
    buttons = []
    letters = ['أ', 'ب', 'ج', 'د']
    for i, option in enumerate(q['ops']):
        buttons.append([InlineKeyboardButton(f"{letters[i]}. {option}", callback_data=f"mcq_{q['id']}_{i}")])
    
    text = f"""
🔴 **سؤال اختيار من متعدد**

📝 {q['q']}
    """
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    q_type, q_id, answer = data[0], int(data[1]), data[2]
    user = query.from_user
    
    if q_type == 'tf':
        q = next((q for q in db.questions['true_false'] if q['id'] == q_id), None)
        if q:
            is_correct = ((answer == 'true') == q['ans'])
            msg = f"✅ **صحيح!**\n\n" if is_correct else f"❌ **خطأ!**\n\n"
            msg += f"💡 {q['exp']}"
            student = db.update_score(user.id, is_correct)
    
    elif q_type == 'mcq':
        q = next((q for q in db.questions['mcq'] if q['id'] == q_id), None)
        if q:
            is_correct = (int(answer) == q['ans'])
            letters = ['أ', 'ب', 'ج', 'د']
            if is_correct:
                msg = f"✅ **إجابة صحيحة!**\n\n💡 {q['exp']}"
            else:
                correct = letters[q['ans']]
                msg = f"❌ **إجابة خاطئة!**\n\n✅ الإجابة الصحيحة: {correct}\n\n💡 {q['exp']}"
            student = db.update_score(user.id, is_correct)
    
    # رسائل تحفيزية
    if is_correct:
        encouragements = [
            "🔥 مذهل! استمر في التقدم!",
            "🚀 رائع! أنت تتفوق!",
            "💪 إجابة ممتازة!",
            "⭐ هذا مستوى متميز!",
            "🎯 دقة عالية!",
        ]
        msg += f"\n\n{random.choice(encouragements)}"
    else:
        reminders = [
            "💡 لا تقلق! كل خطوة تعلّمك شيئاً جديداً",
            "📚 الممارسة تصنع الفرق!",
            "⚡ حاول مرة أخرى، ستنجح!",
        ]
        msg += f"\n\n{random.choice(reminders)}"
    
    # إضافة الإحصائيات
    if student:
        correct = student.get('correct', 0)
        total = student.get('total', 0)
        msg += f"\n\n📊 **إحصائياتك:**\n✅ {correct} صحيح\n📋 {total} إجمالي"
        if total > 0:
            percentage = (correct/total*100)
            msg += f"\n🎯 {percentage:.1f}%"
    
    buttons = [
        [
            InlineKeyboardButton("🔄 صح/خطأ", callback_data="menu_tf"),
            InlineKeyboardButton("🔄 اختيار", callback_data="menu_mcq")
        ],
        [InlineKeyboardButton("🏠 القائمة", callback_data="menu_home")]
    ]
    
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in db.data['students']:
        await update.message.reply_text("⚠️ ابدأ أولاً باستخدام /start")
        return
    
    student = db.data['students'][user_id]
    correct = student.get('correct', 0)
    total = student.get('total', 0)
    level = student.get('level', 1)
    
    msg = f"""
📊 **ملفك الشخصي**

👤 **الاسم:** {student.get('name', 'طالب')}
🎓 **المستوى:** {level}
✅ **إجابات صحيحة:** {correct}
📋 **إجمالي الأسئلة:** {total}
    """
    
    if total > 0:
        percentage = (correct/total*100)
        msg += f"🎯 **نسبة النجاح:** {percentage:.1f}%\n"
        
        # تقييم بناءً على النسبة
        if percentage >= 80:
            msg += "🏅 **تقييم:** ممتاز!"
        elif percentage >= 60:
            msg += "💪 **تقييم:** جيد جداً!"
        else:
            msg += "📚 **تقييم:** جيد - استمر في التدريب!"
    
    msg += f"\n📅 **تاريخ الانضمام:** {student.get('joined', 'غير معروف')}"
    
    await update.message.reply_text(msg)

# 👨🏫 أوامر المعلم (مبسطة وسهلة)
async def add_question_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("❌ هذا الأمر للمعلمين فقط!")
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 صح/خطأ", callback_data="add_tf")],
        [InlineKeyboardButton("🔠 اختيار من متعدد", callback_data="add_mcq")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_add")]
    ])
    
    await update.message.reply_text(
        "👨🏫 **إضافة سؤال جديد**\n\n"
        "اختر نوع السؤال:",
        reply_markup=keyboard
    )

async def view_questions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("❌ هذا الأمر للمعلمين فقط!")
        return
    
    tf_count = len(db.questions['true_false'])
    mcq_count = len(db.questions['mcq'])
    total = tf_count + mcq_count
    
    msg = f"""
📚 **مكتبة الأسئلة**

📊 **الإحصائيات:**
🔵 أسئلة صح/خطأ: {tf_count}
🔴 أسئلة اختيار: {mcq_count}
📋 الإجمالي: {total}

📝 **آخر الأسئلة المضافة:**
    """
    
    # عرض آخر 3 أسئلة من كل نوع
    if tf_count > 0:
        msg += "\n\n🔵 **آخر أسئلة صح/خطأ:**"
        for q in db.questions['true_false'][-3:]:
            answer = "✅ صح" if q['ans'] else "❌ خطأ"
            msg += f"\n• {q['q'][:40]}... ({answer})"
    
    if mcq_count > 0:
        msg += "\n\n🔴 **آخر أسئلة اختيار:**"
        for q in db.questions['mcq'][-3:]:
            msg += f"\n• {q['q'][:40]}..."
    
    await update.message.reply_text(msg)

async def handle_teacher_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "add_tf":
        context.user_data['adding'] = {'type': 'tf', 'step': 1}
        await query.edit_message_text(
            "📝 **أضف سؤال صح/خطأ**\n\n"
            "اكتب نص السؤال:\n\n"
            "مثال: lim┬(x→0)〖sin(x)/x = 1〗"
        )
    
    elif data == "add_mcq":
        context.user_data['adding'] = {'type': 'mcq', 'step': 1}
        await query.edit_message_text(
            "🔠 **أضف سؤال اختيار من متعدد**\n\n"
            "اكتب نص السؤال:\n\n"
            "مثال: ما قيمة lim┬(x→3)〖(x²-9)/(x-3)〗؟"
        )
    
    elif data == "cancel_add":
        await query.edit_message_text("❌ تم إلغاء العملية.")
        if 'adding' in context.user_data:
            del context.user_data['adding']
    
    elif data == "menu_tf":
        await truefalse_command(query, context)
    
    elif data == "menu_mcq":
        await mcq_command(query, context)
    
    elif data == "menu_home":
        await start_command(query, context)

async def handle_teacher_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إضافة الأسئلة من المعلم"""
    if update.effective_user.id != TEACHER_ID:
        return
    
    if 'adding' not in context.user_data:
        return
    
    text = update.message.text.strip()
    adding = context.user_data['adding']
    
    if adding['type'] == 'tf':
        if adding['step'] == 1:
            context.user_data['tf_question'] = text
            context.user_data['adding']['step'] = 2
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ صحيح", callback_data="tf_true")],
                [InlineKeyboardButton("❌ خطأ", callback_data="tf_false")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_add")]
            ])
            
            await update.message.reply_text(
                f"📝 **السؤال:** {text}\n\n"
                "اختر الإجابة الصحيحة:",
                reply_markup=keyboard
            )
    
    elif adding['type'] == 'mcq':
        if adding['step'] == 1:
            context.user_data['mcq_question'] = text
            context.user_data['adding']['step'] = 2
            
            await update.message.reply_text(
                f"🔠 **السؤال:** {text}\n\n"
                "اكتب خيارات الإجابة (مفصولة بفاصلة):\n\n"
                "مثال: 0, 3, 6, 9"
            )

async def handle_tf_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إجابة سؤال صح/خطأ"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "tf_true":
        context.user_data['tf_answer'] = True
    elif query.data == "tf_false":
        context.user_data['tf_answer'] = False
    
    context.user_data['adding']['step'] = 3
    await query.edit_message_text(
        "📝 **اكتب شرح الإجابة:**\n\n"
        "مثال: 'نعم، هذه نهاية أساسية'"
    )

async def handle_mcq_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة خيارات سؤال الاختيار"""
    if update.effective_user.id != TEACHER_ID:
        return
    
    if 'adding' not in context.user_data or context.user_data['adding']['type'] != 'mcq':
        return
    
    if context.user_data['adding']['step'] == 2:
        options = [opt.strip() for opt in update.message.text.split(',') if opt.strip()]
        
        if len(options) < 2:
            await update.message.reply_text("⚠️ أرسل على الأقل خيارين!")
            return
        
        context.user_data['mcq_options'] = options
        context.user_data['adding']['step'] = 3
        
        letters = ['أ', 'ب', 'ج', 'د']
        options_text = "\n".join([f"{letters[i]}. {opt}" for i, opt in enumerate(options)])
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{letters[i]}", callback_data=f"mcq_ans_{i}") for i in range(min(4, len(options)))],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_add")]
        ])
        
        await update.message.reply_text(
            f"🔠 **اختر الإجابة الصحيحة:**\n\n{options_text}",
            reply_markup=keyboard
        )

async def handle_mcq_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إجابة سؤال الاختيار"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("mcq_ans_"):
        answer = int(query.data.split('_')[-1])
        context.user_data['mcq_answer'] = answer
        context.user_data['adding']['step'] = 4
        
        await query.edit_message_text(
            "📝 **اكتب شرح الإجابة:**\n\n"
            "مثال: 'الحل: (x²-9)/(x-3)=x+3، النهاية=6'"
        )

async def handle_explanation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة شرح الإجابة"""
    if update.effective_user.id != TEACHER_ID:
        return
    
    if 'adding' not in context.user_data:
        return
    
    text = update.message.text.strip()
    adding = context.user_data['adding']
    
    if adding['type'] == 'tf' and adding['step'] == 3:
        question = context.user_data['tf_question']
        answer = context.user_data.get('tf_answer', False)
        explanation = text
        
        q_id = db.add_true_false_question(question, answer, explanation)
        
        # تنظيف البيانات
        del context.user_data['adding']
        if 'tf_question' in context.user_data:
            del context.user_data['tf_question']
        if 'tf_answer' in context.user_data:
            del context.user_data['tf_answer']
        
        await update.message.reply_text(
            f"✅ **تم إضافة السؤال بنجاح!**\n\n"
            f"📝 السؤال: {question}\n"
            f"✅ الإجابة: {'صحيح' if answer else 'خطأ'}\n"
            f"📚 رقم السؤال: {q_id}\n\n"
            f"يمكنك إضافة المزيد باستخدام /add_question"
        )
    
    elif adding['type'] == 'mcq' and adding['step'] == 4:
        question = context.user_data['mcq_question']
        options = context.user_data['mcq_options']
        answer = context.user_data['mcq_answer']
        explanation = text
        
        q_id = db.add_mcq_question(question, options, answer, explanation)
        
        # تنظيف البيانات
        del context.user_data['adding']
        if 'mcq_question' in context.user_data:
            del context.user_data['mcq_question']
        if 'mcq_options' in context.user_data:
            del context.user_data['mcq_options']
        if 'mcq_answer' in context.user_data:
            del context.user_data['mcq_answer']
        
        letters = ['أ', 'ب', 'ج', 'د']
        correct_letter = letters[answer] if answer < len(letters) else str(answer)
        
        await update.message.reply_text(
            f"✅ **تم إضافة السؤال بنجاح!**\n\n"
            f"📝 السؤال: {question}\n"
            f"✅ الإجابة الصحيحة: {correct_letter}\n"
            f"📚 رقم السؤال: {q_id}\n\n"
            f"يمكنك إضافة المزيد باستخدام /add_question"
        )

# 🔧 تشغيل Flask
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# 🤖 تشغيل البوت الرئيسي
async def run_bot():
    print("=" * 50)
    print("🤖 بوت اختبارات الرياضيات - نسخة مستقرة")
    print("=" * 50)
    print(f"📅 بدأ التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"👥 الطلاب المسجلين: {len(db.data['students'])}")
    print(f"📚 الأسئلة: {len(db.questions['true_false'])} صح/خطأ، {len(db.questions['mcq'])} اختيار")
    print("=" * 50)
    
    # إنشاء تطبيق البوت
    application = Application.builder().token(TOKEN).build()
    
    # إضافة Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("truefalse", truefalse_command))
    application.add_handler(CommandHandler("mcq", mcq_command))
    application.add_handler(CommandHandler("score", score_command))
    application.add_handler(CommandHandler("add_question", add_question_command))
    application.add_handler(CommandHandler("view_questions", view_questions_command))
    
    # Callback Handlers
    application.add_handler(CallbackQueryHandler(handle_answer, pattern="^(tf|mcq)_"))
    application.add_handler(CallbackQueryHandler(handle_teacher_callback, pattern="^(add_|cancel_|menu_|tf_|mcq_)"))
    application.add_handler(CallbackQueryHandler(handle_tf_answer, pattern="^(tf_true|tf_false)$"))
    application.add_handler(CallbackQueryHandler(handle_mcq_answer, pattern="^mcq_ans_"))
    
    # Message Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(TEACHER_ID), handle_teacher_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(TEACHER_ID), handle_mcq_options))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(TEACHER_ID), handle_explanation))
    
    try:
        # بدء البوت
        await application.initialize()
        await application.start()
        
        print("✅ البوت بدأ التشغيل بنجاح!")
        
        # Polling
        await application.updater.start_polling()
        
        # إبقاء البرنامج يعمل
        while True:
            await asyncio.sleep(3600)
            
    except Conflict:
        print("⚠️ تحذير: يوجد نسخة أخرى من البوت تعمل.")
        print("✅ الحل: اذهب إلى Render وأعد تشغيل الخدمة.")
        await application.stop()
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        await application.stop()

# 🚀 التشغيل الرئيسي
if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # انتظار 3 ثوانٍ ثم تشغيل البوت
    time.sleep(3)
    
    # تشغيل البوت
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت.")
