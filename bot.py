# 🧮 بوت اختبارات رياضيات النهايات - مع إدارة الأسئلة للمعلم
# 🔧 يعمل 24/7 على Render

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

# 🔐 التوكن من متغيرات البيئة
TOKEN = os.environ.get('TELEGRAM_TOKEN')
TEACHER_ID = 8422436251  # غير هذا الرقم إلى ID الخاص بك

# 🌐 Flask لإبقاء البوت نشطاً
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>بوت الرياضيات</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; }
                h1 { color: #2c3e50; }
                .status { color: #27ae60; font-size: 24px; }
            </style>
        </head>
        <body>
            <h1>🤖 بوت اختبارات الرياضيات</h1>
            <div class="status">✅ يعمل بنجاح!</div>
            <p>⏰ يعمل 24/7 على Render</p>
            <p>👨🏫 للمعلم: استخدم /add_question لإضافة أسئلة جديدة</p>
            <p>📱 للطلاب: ابحث عن @mathimatical_testBot</p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "active", "timestamp": datetime.now().isoformat()}

@app.route('/ping')
def ping():
    return "pong"

# 🔄 وظيفة لإرسال طلبات دورية
def keep_alive():
    """إبقاء البوت نشطاً بإرسال طلبات دورية"""
    def ping_server():
        while True:
            try:
                # الحصول على رابط Render تلقائياً
                render_url = os.environ.get('RENDER_URL', '')
                if not render_url:
                    # محاولة تخمين الرابط
                    service_name = os.environ.get('RENDER_SERVICE_NAME', '')
                    if service_name:
                        render_url = f"https://{service_name}.onrender.com"
                
                if render_url:
                    response = requests.get(f"{render_url}/ping", timeout=10)
                    print(f"✅ Keep-alive ping: {response.status_code} at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    print("⚠️ لا يمكن تحديد رابط Render")
            except Exception as e:
                print(f"⚠️ Keep-alive failed: {e}")
            time.sleep(300)  # كل 5 دقائق
    
    thread = threading.Thread(target=ping_server, daemon=True)
    thread.start()

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
            # الأسئلة الافتراضية
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
                'last_active': datetime.now().isoformat()
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
        """إضافة سؤال صح/خطأ جديد"""
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
        """إضافة سؤال اختيار من متعدد جديد"""
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
    
    def delete_question(self, q_type, q_id):
        """حذف سؤال"""
        q_id = int(q_id)
        if q_type == 'tf':
            self.questions['true_false'] = [q for q in self.questions['true_false'] if q['id'] != q_id]
        elif q_type == 'mcq':
            self.questions['mcq'] = [q for q in self.questions['mcq'] if q['id'] != q_id]
        self.save_questions()
    
    def get_questions_summary(self):
        """الحصول على ملخص للأسئلة"""
        return {
            'true_false': len(self.questions['true_false']),
            'mcq': len(self.questions['mcq'])
        }

db = Database()

# 🎯 دوال البوت الأساسية
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.register_student(user.id, user.first_name)
    
    if is_new:
        msg = f"🎉 أهلاً {user.first_name}!\nتم تسجيلك في بوت اختبارات النهايات."
    else:
        student = db.data['students'].get(str(user.id), {})
        msg = f"👋 أهلًا بعودتك {user.first_name}!\nنتيجتك: {student.get('correct', 0)}/{student.get('total', 0)}"
    
    msg += "\n\n📋 الأوامر:\n/start - البداية\n/truefalse - أسئلة صح/خطأ\n/mcq - أسئلة خيارات\n/score - نتيجتك\n/top - المتصدرين"
    
    if user.id == TEACHER_ID:
        msg += "\n\n👨🏫 أوامر المعلم:\n/add_question - إضافة سؤال جديد\n/view_questions - عرض الأسئلة\n/delete_question - حذف سؤال"
    
    await update.message.reply_text(msg)

async def truefalse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.questions['true_false']:
        await update.message.reply_text("⚠️ لا توجد أسئلة صح/خطأ متاحة حالياً.")
        return
    
    q = random.choice(db.questions['true_false'])
    buttons = [
        [InlineKeyboardButton("✅ صحيح", callback_data=f"tf_{q['id']}_true")],
        [InlineKeyboardButton("❌ خطأ", callback_data=f"tf_{q['id']}_false")]
    ]
    text = f"🔵 سؤال صح/خطأ:\n\n❓ {q['q']}"
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
    text = f"🔴 سؤال خيارات:\n\n❓ {q['q']}"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    q_type, q_id, answer = data[0], int(data[1]), data[2]
    
    if q_type == 'tf':
        q = next((q for q in db.questions['true_false'] if q['id'] == q_id), None)
        if q:
            is_correct = ((answer == 'true') == q['ans'])
            msg = f"✅ صحيح!\n\n{q['exp']}" if is_correct else f"❌ خطأ!\n\n{q['exp']}"
            db.update_score(query.from_user.id, is_correct)
    
    elif q_type == 'mcq':
        q = next((q for q in db.questions['mcq'] if q['id'] == q_id), None)
        if q:
            is_correct = (int(answer) == q['ans'])
            letters = ['أ', 'ب', 'ج', 'د']
            if is_correct:
                msg = f"✅ إجابة صحيحة!\n\n{q['exp']}"
            else:
                correct = letters[q['ans']]
                msg = f"❌ إجابة خاطئة!\nالصحيحة: {correct}\n\n{q['exp']}"
            db.update_score(query.from_user.id, is_correct)
    
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
    total, correct = student['total'], student['correct']
    percent = (correct/total*100) if total > 0 else 0
    
    report = f"📊 نتيجتك:\n✅ {correct} صحيح\n❌ {total-correct} خطأ\n🎯 {percent:.1f}%\n📅 {student['joined']}"
    await update.message.reply_text(report)

# 👨🏫 أوامر المعلم
async def add_question_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية إضافة سؤال جديد"""
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("❌ هذا الأمر للمعلم فقط!")
        return
    
    buttons = [
        [InlineKeyboardButton("📝 صح/خطأ", callback_data="add_tf")],
        [InlineKeyboardButton("🔠 اختيار من متعدد", callback_data="add_mcq")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_add")]
    ]
    
    await update.message.reply_text(
        "👨🏫 اختر نوع السؤال الذي تريد إضافته:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def view_questions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض ملخص الأسئلة"""
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("❌ هذا الأمر للمعلم فقط!")
        return
    
    summary = db.get_questions_summary()
    tf_questions = db.questions['true_false']
    mcq_questions = db.questions['mcq']
    
    message = f"📚 ملخص الأسئلة:\n\n"
    message += f"📝 أسئلة صح/خطأ: {summary['true_false']}\n"
    message += f"🔠 أسئلة اختيار من متعدد: {summary['mcq']}\n\n"
    
    if tf_questions:
        message += "📝 أسئلة صح/خطأ:\n"
        for q in tf_questions[:5]:  # عرض أول 5 أسئلة فقط
            answer = "✅ صحيح" if q['ans'] else "❌ خطأ"
            message += f"{q['id']}. {q['q'][:50]}... ({answer})\n"
    
    if mcq_questions:
        message += "\n🔠 أسئلة اختيار من متعدد:\n"
        for q in mcq_questions[:5]:  # عرض أول 5 أسئلة فقط
            message += f"{q['id']}. {q['q'][:50]}...\n"
    
    await update.message.reply_text(message)

async def delete_question_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية حذف سؤال"""
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("❌ هذا الأمر للمعلم فقط!")
        return
    
    summary = db.get_questions_summary()
    
    buttons = []
    if summary['true_false'] > 0:
        buttons.append([InlineKeyboardButton(f"📝 حذف سؤال صح/خطأ ({summary['true_false']})", callback_data="delete_tf")])
    if summary['mcq'] > 0:
        buttons.append([InlineKeyboardButton(f"🔠 حذف سؤال اختيار ({summary['mcq']})", callback_data="delete_mcq")])
    
    if not buttons:
        await update.message.reply_text("⚠️ لا توجد أسئلة للحذف!")
        return
    
    buttons.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_delete")])
    
    await update.message.reply_text(
        "🗑️ اختر نوع السؤال الذي تريد حذفه:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_teacher_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إجراءات المعلم"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "add_tf":
        context.user_data['adding_question'] = {'type': 'tf', 'step': 'question'}
        await query.edit_message_text(
            "📝 أرسل نص سؤال الصح/خطأ:\n\n"
            "مثال: lim┬(x→0)〖sin(x)/x = 1〗"
        )
    
    elif data == "add_mcq":
        context.user_data['adding_question'] = {'type': 'mcq', 'step': 'question'}
        await query.edit_message_text(
            "🔠 أرسل نص سؤال الاختيار من متعدد:\n\n"
            "مثال: ما قيمة: lim┬(x→3)〖(x²-9)/(x-3)〗؟"
        )
    
    elif data.startswith("delete_tf"):
        if data == "delete_tf":
            # عرض قائمة أسئلة الصح/خطأ للحذف
            tf_questions = db.questions['true_false']
            buttons = []
            for q in tf_questions:
                buttons.append([InlineKeyboardButton(
                    f"🗑️ {q['id']}. {q['q'][:30]}...",
                    callback_data=f"confirm_delete_tf_{q['id']}"
                )])
            buttons.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_delete")])
            
            await query.edit_message_text(
                "اختر السؤال الذي تريد حذفه:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        elif data.startswith("confirm_delete_tf_"):
            q_id = data.split('_')[-1]
            db.delete_question('tf', q_id)
            await query.edit_message_text(f"✅ تم حذف السؤال رقم {q_id} بنجاح!")
    
    elif data.startswith("delete_mcq"):
        if data == "delete_mcq":
            # عرض قائمة أسئلة الاختيار للحذف
            mcq_questions = db.questions['mcq']
            buttons = []
            for q in mcq_questions:
                buttons.append([InlineKeyboardButton(
                    f"🗑️ {q['id']}. {q['q'][:30]}...",
                    callback_data=f"confirm_delete_mcq_{q['id']}"
                )])
            buttons.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_delete")])
            
            await query.edit_message_text(
                "اختر السؤال الذي تريد حذفه:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        elif data.startswith("confirm_delete_mcq_"):
            q_id = data.split('_')[-1]
            db.delete_question('mcq', q_id)
            await query.edit_message_text(f"✅ تم حذف السؤال رقم {q_id} بنجاح!")
    
    elif data == "cancel_add" or data == "cancel_delete":
        await query.edit_message_text("❌ تم الإلغاء.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل النصية لإضافة الأسئلة"""
    if update.effective_user.id != TEACHER_ID:
        return
    
    if 'adding_question' not in context.user_data:
        return
    
    adding = context.user_data['adding_question']
    text = update.message.text
    
    if adding['type'] == 'tf':
        if adding['step'] == 'question':
            context.user_data['tf_question'] = text
            context.user_data['adding_question']['step'] = 'answer'
            await update.message.reply_text(
                "💡 هل الإجابة صحيحة أم خاطئة؟\n\n"
                "أرسل: 'صح' أو 'خطأ'"
            )
        
        elif adding['step'] == 'answer':
            if text.lower() in ['صح', 'صحيح', 'true']:
                answer = True
            elif text.lower() in ['خطأ', 'خطا', 'false']:
                answer = False
            else:
                await update.message.reply_text("⚠️ أرسل 'صح' أو 'خطأ' فقط!")
                return
            
            context.user_data['tf_answer'] = answer
            context.user_data['adding_question']['step'] = 'explanation'
            await update.message.reply_text(
                "📝 أرسل شرح الإجابة:\n\n"
                "مثال: 'نعم، هذه نهاية أساسية'"
            )
        
        elif adding['step'] == 'explanation':
            question = context.user_data['tf_question']
            answer = context.user_data['tf_answer']
            explanation = text
            
            q_id = db.add_true_false_question(question, answer, explanation)
            
            # تنظيف البيانات المؤقتة
            del context.user_data['adding_question']
            del context.user_data['tf_question']
            del context.user_data['tf_answer']
            
            await update.message.reply_text(
                f"✅ تم إضافة السؤال بنجاح!\n\n"
                f"📝 السؤال: {question}\n"
                f"✅ الإجابة: {'صحيح' if answer else 'خطأ'}\n"
                f"📚 رقم السؤال: {q_id}\n\n"
                f"يمكنك إضافة المزيد باستخدام /add_question"
            )
    
    elif adding['type'] == 'mcq':
        if adding['step'] == 'question':
            context.user_data['mcq_question'] = text
            context.user_data['adding_question']['step'] = 'options'
            await update.message.reply_text(
                "🔤 أرسل خيارات الإجابة (كل خيار في سطر منفصل):\n\n"
                "مثال:\n"
                "0\n"
                "3\n"
                "6\n"
                "9"
            )
        
        elif adding['step'] == 'options':
            options = [opt.strip() for opt in text.split('\n') if opt.strip()]
            if len(options) < 2:
                await update.message.reply_text("⚠️ أرسل على الأقل خيارين!")
                return
            
            context.user_data['mcq_options'] = options
            context.user_data['adding_question']['step'] = 'answer'
            
            letters = ['أ', 'ب', 'ج', 'د', 'ه', 'و']
            options_text = "\n".join([f"{letters[i]}. {opt}" for i, opt in enumerate(options[:6])])
            
            await update.message.reply_text(
                f"🔠 اختر رقم الإجابة الصحيحة (بدءاً من 0):\n\n"
                f"{options_text}\n\n"
                f"أرسل الرقم فقط (مثال: 2)"
            )
        
        elif adding['step'] == 'answer':
            try:
                answer = int(text)
                options = context.user_data['mcq_options']
                if answer < 0 or answer >= len(options):
                    await update.message.reply_text(f"⚠️ الرقم يجب أن يكون بين 0 و {len(options)-1}!")
                    return
                
                context.user_data['mcq_answer'] = answer
                context.user_data['adding_question']['step'] = 'explanation'
                await update.message.reply_text(
                    "📝 أرسل شرح الإجابة:\n\n"
                    "مثال: 'الحل: (x²-9)/(x-3)=x+3، النهاية=6'"
                )
            except ValueError:
                await update.message.reply_text("⚠️ أرسل رقماً صحيحاً فقط!")
        
        elif adding['step'] == 'explanation':
            question = context.user_data['mcq_question']
            options = context.user_data['mcq_options']
            answer = context.user_data['mcq_answer']
            explanation = text
            
            q_id = db.add_mcq_question(question, options, answer, explanation)
            
            # تنظيف البيانات المؤقتة
            del context.user_data['adding_question']
            del context.user_data['mcq_question']
            del context.user_data['mcq_options']
            del context.user_data['mcq_answer']
            
            letters = ['أ', 'ب', 'ج', 'د', 'ه', 'و']
            answer_text = letters[answer] if answer < len(letters) else str(answer)
            
            await update.message.reply_text(
                f"✅ تم إضافة السؤال بنجاح!\n\n"
                f"📝 السؤال: {question}\n"
                f"✅ الإجابة الصحيحة: {answer_text}\n"
                f"📚 رقم السؤال: {q_id}\n\n"
                f"يمكنك إضافة المزيد باستخدام /add_question"
            )

# 🔧 تشغيل Flask في خيط منفصل
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# 🔧 تشغيل البوت
def run_telegram_bot():
    print("=" * 50)
    print("🧮 بوت اختبارات رياضيات النهايات")
    print("=" * 50)
    print(f"📅 بدأ التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"👥 الطلاب المسجلين: {len(db.data['students'])}")
    
    summary = db.get_questions_summary()
    print(f"📚 الأسئلة: {summary['true_false']} صح/خطأ، {summary['mcq']} اختيار من متعدد")
    print("✅ البوت يعمل 24/7 مع Keep-alive!")
    print("👨🏫 خاصية إضافة الأسئلة للمعلم مفعلة")
    print("=" * 50)
    
    # بدء Keep-alive
    keep_alive()
    
    # تشغيل البوت
    async def main():
        app = Application.builder().token(TOKEN).build()
        
        # أوامر الطلاب
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("truefalse", truefalse_command))
        app.add_handler(CommandHandler("mcq", mcq_command))
        app.add_handler(CommandHandler("score", score_command))
        
        # أوامر المعلم
        app.add_handler(CommandHandler("add_question", add_question_command))
        app.add_handler(CommandHandler("view_questions", view_questions_command))
        app.add_handler(CommandHandler("delete_question", delete_question_command))
        
        # معالجات Callback
        app.add_handler(CallbackQueryHandler(handle_answer, pattern="^tf_"))
        app.add_handler(CallbackQueryHandler(handle_answer, pattern="^mcq_"))
        app.add_handler(CallbackQueryHandler(handle_teacher_actions, pattern="^(add_|delete_|confirm_|cancel_)"))
        
        # معالجة الرسائل النصية (لإضافة الأسئلة)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # استمر في التشغيل
        while True:
            await asyncio.sleep(3600)
    
    asyncio.run(main())

# 🚀 نقطة البداية
if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # تشغيل البوت بعد ثانيتين
    time.sleep(2)
    run_telegram_bot()
