# 🧮 بوت اختبارات رياضيات النهايات - واجهة محسنة
# 🎨 تصميم عربي جميل مع رسائل تحفيزية
# 👨🏫 واجهة سهلة لإضافة الأسئلة للمعلم

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
TEACHER_ID = 8422436251  # ❗ غير هذا الرقم إلى ID الخاص بك!

# 🌐 Flask لإبقاء البوت نشطاً
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>بوت الرياضيات التفاعلي</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: rgba(255, 255, 255, 0.95); 
                    padding: 40px; 
                    border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                h1 { 
                    color: #2c3e50; 
                    font-size: 2.5em; 
                    margin-bottom: 20px;
                    background: linear-gradient(to right, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .emoji { font-size: 3em; margin: 20px; }
                .status { 
                    color: #27ae60; 
                    font-size: 28px; 
                    font-weight: bold;
                    padding: 15px;
                    background: #e8f5e9;
                    border-radius: 10px;
                    margin: 20px 0;
                }
                .features { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; 
                    margin: 40px 0; 
                }
                .feature-card { 
                    background: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s;
                }
                .feature-card:hover { transform: translateY(-5px); }
                .feature-card h3 { color: #2c3e50; margin-bottom: 10px; }
                .feature-card p { color: #7f8c8d; }
                .btn { 
                    display: inline-block; 
                    padding: 12px 30px; 
                    margin: 10px; 
                    background: linear-gradient(to right, #667eea, #764ba2);
                    color: white; 
                    text-decoration: none; 
                    border-radius: 25px; 
                    font-weight: bold;
                    transition: all 0.3s;
                }
                .btn:hover { 
                    transform: scale(1.05); 
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }
                .stats { 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 15px; 
                    margin-top: 30px;
                    color: #2c3e50;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">🧮🤖✨</div>
                <h1>بوت اختبارات الرياضيات التفاعلي</h1>
                <div class="status">✅ البوت يعمل بنجاح!</div>
                
                <div class="features">
                    <div class="feature-card">
                        <h3>🎯 للطلاب</h3>
                        <p>اختبارات تفاعلية في النهايات</p>
                        <p>نتائج فورية وتصحيح آلي</p>
                        <p>تصنيفات وتحفيز مستمر</p>
                    </div>
                    <div class="feature-card">
                        <h3>👨🏫 للمعلمين</h3>
                        <p>إدارة أسئلة سهلة وسريعة</p>
                        <p>إحصائيات مفصلة</p>
                        <p>متابعة مستوى الطلاب</p>
                    </div>
                    <div class="feature-card">
                        <h3>⚡ مميزات</h3>
                        <p>يعمل 24/7</p>
                        <p>واجهة عربية سلسة</p>
                        <p>أسئلة متنوعة</p>
                    </div>
                </div>
                
                <div style="margin: 40px 0;">
                    <p style="color: #2c3e50; font-size: 1.1em;">
                        📱 للطلاب: ابحث عن <strong>@mathimatical_testBot</strong> في التليجرام<br>
                        👨🏫 للمعلم: استخدم أوامر خاصة لإدارة الأسئلة
                    </p>
                </div>
                
                <div class="stats">
                    <h3>📊 البوت يعمل الآن على:</h3>
                    <p>🌐 <strong>https://telegram-quiz-bot-7.onrender.com</strong></p>
                    <p>🕐 آخر تحديث: <span id="time"></span></p>
                </div>
            </div>
            
            <script>
                document.getElementById('time').textContent = new Date().toLocaleString('ar-SA');
                setInterval(() => {
                    document.getElementById('time').textContent = new Date().toLocaleString('ar-SA');
                }, 1000);
            </script>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "active", "timestamp": datetime.now().isoformat()}

@app.route('/ping')
def ping():
    return "pong"

# 🌟 رسائل تحفيزية للطلاب
ENCOURAGEMENTS = [
    "🔥 مذهل! أنت تفهم الموضوع بشكل رائع!",
    "🚀 إجابة صحيحة! استمر في التقدم!",
    "💪 رائع! مهاراتك الرياضية ممتازة!",
    "⭐ نجاح باهر! هذا مستوى متميز!",
    "🎯 دقة عالية! أنت على الطريق الصحيح!",
    "✨ إبداع! طريقة تفكيرك رائعة!",
    "🏆 إجابة مثالية! أنت تتفوق على نفسك!",
    "📈 تقدم مذهل! استمر في التعلم!",
    "💫 مهارة خارقة! النهايات ليست صعبة عليك!",
    "👑 تفوق! أنت من صناع النجاح!",
]

REMINDERS = [
    "💡 تذكر: النهايات هي أساس التفاضل والتكامل!",
    "📚 الممارسة المستمرة هي سر التميز في الرياضيات!",
    "🎓 كل سؤال تحله يقربك أكثر من الإتقان!",
    "⚡ لا تستسلم، الرياضيات تحتاج إلى صبر ومثابرة!",
    "🌟 أنت قادر على فهم أصعب النهايات!",
]

# 📊 قاعدة البيانات
class Database:
    def __init__(self):
        self.data_file = 'data.json'
        self.questions_file = 'questions.json'
        self.streaks_file = 'streaks.json'
        self.data = self.load_data()
        self.questions = self.load_questions()
        self.streaks = self.load_streaks()
    
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
    
    def load_streaks(self):
        try:
            with open(self.streaks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def save_questions(self, questions=None):
        if questions is None:
            questions = self.questions
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    
    def save_streaks(self):
        with open(self.streaks_file, 'w', encoding='utf-8') as f:
            json.dump(self.streaks, f, ensure_ascii=False, indent=2)
    
    def register_student(self, user_id, name):
        user_id = str(user_id)
        if user_id not in self.data['students']:
            self.data['students'][user_id] = {
                'name': name,
                'correct': 0,
                'total': 0,
                'joined': datetime.now().strftime('%Y-%m-%d'),
                'last_active': datetime.now().isoformat(),
                'level': 1,
                'xp': 0,
                'streak': 0
            }
            self.save_data()
            return True
        return False
    
    def update_score(self, user_id, is_correct):
        user_id = str(user_id)
        if user_id in self.data['students']:
            student = self.data['students'][user_id]
            student['total'] += 1
            student['last_active'] = datetime.now().isoformat()
            
            if is_correct:
                student['correct'] += 1
                student['xp'] += 10
                student['streak'] = student.get('streak', 0) + 1
                
                # مكافآت streak
                if student['streak'] % 5 == 0:
                    student['xp'] += 25
                
                # ترقية المستوى
                if student['xp'] >= student['level'] * 100:
                    student['level'] += 1
                    student['xp'] = 0
            else:
                student['streak'] = 0
            
            self.data['total_questions'] += 1
            if is_correct:
                self.data['correct_answers'] += 1
            
            self.save_data()
            return student
    
    def get_encouragement(self):
        return random.choice(ENCOURAGEMENTS)
    
    def get_reminder(self):
        return random.choice(REMINDERS)
    
    def get_streak_message(self, streak):
        if streak >= 10:
            return f"🔥🔥🔥 سلسلة إجابات صحيحة: {streak}! أنت لا تخطئ!"
        elif streak >= 5:
            return f"🔥🔥 سلسلة إجابات صحيحة: {streak}! استمر هكذا!"
        elif streak >= 3:
            return f"🔥 سلسلة إجابات صحيحة: {streak}! ممتاز!"
        return ""

db = Database()

# 🎨 وظائف مساعدة للتصميم
def create_menu_buttons():
    """إنشاء أزرار القائمة الرئيسية"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 اختبر نفسك", callback_data="start_quiz"),
            InlineKeyboardButton("📊 نتيجتي", callback_data="my_score")
        ],
        [
            InlineKeyboardButton("🏆 المتصدرين", callback_data="leaderboard"),
            InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")
        ]
    ])

def create_quiz_type_buttons():
    """إنشاء أزرار أنواع الاختبارات"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵 صح/خطأ", callback_data="quiz_tf"),
            InlineKeyboardButton("🔴 اختيار من متعدد", callback_data="quiz_mcq")
        ],
        [
            InlineKeyboardButton("📋 مختلط", callback_data="quiz_mixed"),
            InlineKeyboardButton("🏃🏻 اختبار سريع", callback_data="quiz_quick")
        ],
        [
            InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
        ]
    ])

def create_teacher_menu():
    """إنشاء قائمة المعلم"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ أضف سؤالاً", callback_data="teacher_add"),
            InlineKeyboardButton("👁️ عرض الأسئلة", callback_data="teacher_view")
        ],
        [
            InlineKeyboardButton("📊 الإحصائيات", callback_data="teacher_stats"),
            InlineKeyboardButton("🗑️ حذف أسئلة", callback_data="teacher_delete")
        ],
        [
            InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")
        ]
    ])

def format_question_box(question, q_type="🔵"):
    """تنسيق مربع السؤال"""
    border = "━" * 30
    return f"""
{border}
{q_type} الســـؤال
{border}

📝 {question}

{border}
    """

def format_answer_box(is_correct, message):
    """تنسيق مربع الإجابة"""
    if is_correct:
        border = "━" * 30
        return f"""
{border}
✅ الإجـابـة الصـحـيـحـة
{border}

✨ {message}

{border}
        """
    else:
        border = "━" * 30
        return f"""
{border}
❌ إجـابـة خـاطـئـة
{border}

💡 {message}

{border}
        """

# 🎯 دوال البوت الرئيسية
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.register_student(user.id, user.first_name)
    
    welcome_msg = f"""
✨✨✨✨✨✨✨✨✨✨✨✨
       مــرحــبــاً {user.first_name}!
✨✨✨✨✨✨✨✨✨✨✨✨

🎯 **بوت اختبارات النهايات التفاعلي**

📚 اختبر مهاراتك في النهايات
⚡ احصل على تقييم فوري
🏆 تقدم في التصنيفات
    """
    
    if is_new:
        welcome_msg += f"\n🎉 **تم تسجيلك بنجاح في النظام!**"
    else:
        student = db.data['students'].get(str(user.id), {})
        welcome_msg += f"\n👋 **أهلًا بعودتك!**"
        welcome_msg += f"\n📊 مستواك: {student.get('level', 1)} ⭐"
        welcome_msg += f"\n🎯 نتيجتك: {student.get('correct', 0)}/{student.get('total', 0)}"
    
    welcome_msg += f"\n\n{db.get_reminder()}"
    
    if user.id == TEACHER_ID:
        welcome_msg += "\n\n👨🏫 **أنت مسجل كمدرس** - يمكنك إدارة الأسئلة"
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=create_menu_buttons()
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "main_menu":
        user = query.from_user
        msg = f"""
📋 **القائمة الرئيسية**

اختر أحد الخيارات:
        """
        await query.edit_message_text(
            msg,
            reply_markup=create_menu_buttons()
        )
    
    elif data == "start_quiz":
        msg = """
🎯 **اختر نوع الاختبار**

🔵 **صح/خطأ**: اختبر فهمك للمفاهيم
🔴 **اختيار من متعدد**: تدرب على الحلول
📋 **مختلط**: مزيج من الأنواع
🏃🏻 **سريع**: 5 أسئلة في دقيقة
        """
        await query.edit_message_text(
            msg,
            reply_markup=create_quiz_type_buttons()
        )
    
    elif data == "quiz_tf":
        await truefalse_quiz(update, context)
    
    elif data == "quiz_mcq":
        await mcq_quiz(update, context)
    
    elif data == "my_score":
        await show_score(update, context)
    
    elif data == "teacher_menu":
        if query.from_user.id == TEACHER_ID:
            msg = """
👨🏫 **لوحة تحكم المعلم**

اختر المهمة التي تريد تنفيذها:
            """
            await query.edit_message_text(
                msg,
                reply_markup=create_teacher_menu()
            )
        else:
            await query.edit_message_text("❌ هذا القسم للمعلمين فقط!")

async def truefalse_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not db.questions['true_false']:
        await query.edit_message_text("⚠️ لا توجد أسئلة صح/خطأ متاحة حالياً.")
        return
    
    q = random.choice(db.questions['true_false'])
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ صحيح", callback_data=f"answer_tf_{q['id']}_true"),
            InlineKeyboardButton("❌ خطأ", callback_data=f"answer_tf_{q['id']}_false")
        ],
        [
            InlineKeyboardButton("🔙 رجوع", callback_data="start_quiz")
        ]
    ])
    
    question_text = format_question_box(q['q'], "🔵 سؤال صح/خطأ")
    await query.edit_message_text(
        question_text,
        reply_markup=buttons
    )

async def mcq_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not db.questions['mcq']:
        await query.edit_message_text("⚠️ لا توجد أسئلة اختيار من متعدد متاحة حالياً.")
        return
    
    q = random.choice(db.questions['mcq'])
    
    buttons = []
    letters = ['أ', 'ب', 'ج', 'د', 'ه', 'و']
    for i, option in enumerate(q['ops']):
        buttons.append([
            InlineKeyboardButton(
                f"{letters[i]}. {option}",
                callback_data=f"answer_mcq_{q['id']}_{i}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton("🔙 رجوع", callback_data="start_quiz")
    ])
    
    question_text = format_question_box(q['q'], "🔴 سؤال اختيار من متعدد")
    await query.edit_message_text(
        question_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    q_type, q_id, answer = data[1], int(data[2]), data[3]
    
    if q_type == "tf":
        q = next((q for q in db.questions['true_false'] if q['id'] == q_id), None)
        if q:
            is_correct = ((answer == 'true') == q['ans'])
            explanation = q['exp']
            student = db.update_score(query.from_user.id, is_correct)
    
    elif q_type == "mcq":
        q = next((q for q in db.questions['mcq'] if q['id'] == q_id), None)
        if q:
            is_correct = (int(answer) == q['ans'])
            letters = ['أ', 'ب', 'ج', 'د', 'ه', 'و']
            if is_correct:
                explanation = q['exp']
            else:
                correct_letter = letters[q['ans']]
                explanation = f"الإجابة الصحيحة: {correct_letter}\n\n{q['exp']}"
            student = db.update_score(query.from_user.id, is_correct)
    
    # إنشاء رسالة النتيجة
    result_msg = ""
    
    if is_correct:
        result_msg += format_answer_box(True, db.get_encouragement())
        result_msg += f"\n💡 **شرح الإجابة:**\n{explanation}"
        
        # إضافة رسالة streak
        streak_msg = db.get_streak_message(student.get('streak', 0))
        if streak_msg:
            result_msg += f"\n\n{streak_msg}"
    else:
        result_msg += format_answer_box(False, "لا تقلق! كل خطوة تعلّمك شيئاً جديداً")
        result_msg += f"\n💡 **التصحيح:**\n{explanation}"
        result_msg += f"\n\n{db.get_reminder()}"
    
    # إضافة الإحصائيات
    result_msg += f"\n\n📊 **إحصائياتك:**"
    result_msg += f"\n✅ إجابات صحيحة: {student.get('correct', 0)}"
    result_msg += f"\n🎯 مستوى: {student.get('level', 1)} ⭐"
    result_msg += f"\n🔥 نقاط خبرة: {student.get('xp', 0)} XP"
    result_msg += f"\n📈 نسبة النجاح: {(student.get('correct', 0)/student.get('total', 1)*100):.1f}%"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 سؤال آخر", callback_data="start_quiz"),
            InlineKeyboardButton("📊 نتيجتي", callback_data="my_score")
        ],
        [
            InlineKeyboardButton("📋 القائمة الرئيسية", callback_data="main_menu")
        ]
    ])
    
    await query.edit_message_text(
        result_msg,
        reply_markup=buttons
    )

async def show_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    if user_id not in db.data['students']:
        await query.edit_message_text("⚠️ ابدأ أولاً باستخدام /start")
        return
    
    student = db.data['students'][user_id]
    total = student.get('total', 0)
    correct = student.get('correct', 0)
    level = student.get('level', 1)
    xp = student.get('xp', 0)
    streak = student.get('streak', 0)
    
    # حساب التقدم نحو المستوى التالي
    next_level_xp = level * 100
    progress = (xp / next_level_xp) * 100 if next_level_xp > 0 else 0
    
    # شريط التقدم
    progress_bar = "[" + "▓" * int(progress/10) + "░" * (10 - int(progress/10)) + "]"
    
    score_msg = f"""
📊 **ملفك الشخصي**

👤 **الاسم:** {student.get('name', 'طالب')}
🎓 **المستوى:** {level} ⭐
🔥 **نقاط الخبرة:** {xp} / {next_level_xp} XP
{progress_bar} {progress:.1f}%

🏆 **الإنجازات:**
✅ إجابات صحيحة: {correct}
📋 إجمالي الأسئلة: {total}
🎯 نسبة النجاح: {(correct/total*100):.1f}% if total > 0 else 0
🔥 سلسلة إجابات صحيحة: {streak}

📅 **تاريخ الانضمام:** {student.get('joined', 'غير معروف')}
📈 **آخر نشاط:** {datetime.fromisoformat(student.get('last_active')).strftime('%Y-%m-%d %H:%M') if student.get('last_active') else 'غير معروف'}
    """
    
    # رسالة تحفيزية بناءً على النسبة
    if total > 0:
        percentage = (correct/total*100)
        if percentage >= 80:
            score_msg += "\n\n🏅 **ممتاز!** أنت تتفوق في النهايات!"
        elif percentage >= 60:
            score_msg += "\n\n💪 **جيد جداً!** استمر في الممارسة!"
        else:
            score_msg += "\n\n📚 **جيد!** المزيد من التدريب سيجعلك متميزاً!"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 اختبر نفسك", callback_data="start_quiz"),
            InlineKeyboardButton("🏆 المتصدرين", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")
        ]
    ])
    
    await query.edit_message_text(
        score_msg,
        reply_markup=buttons
    )

# 👨🏫 واجهة المعلم السهلة
async def teacher_add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية إضافة سؤال بطريقة سهلة"""
    query = update.callback_query
    await query.answer()
    
    msg = """
👨🏫 **إضافة سؤال جديد**

📝 **طريقة سهلة:**
أرسل السؤال كاملاً في رسالة واحدة بهذا الشكل:

🔵 **للسؤال صح/خطأ:**
السؤال | الجواب (صح/خطأ) | الشرح

مثال:
lim┬(x→0)〖sin(x)/x = 1〗 | صح | هذه نهاية أساسية

🔴 **لأسئلة الاختيار:**
السؤال | الخيار1,الخيار2,الخيار3,الخيار4 | رقم الإجابة الصحيحة (0,1,2,3) | الشرح

مثال:
ما قيمة lim┬(x→3)〖(x²-9)/(x-3)〗؟ | 0,3,6,9 | 2 | (x²-9)/(x-3)=x+3، النهاية=6

📌 **ملاحظات:**
• استخدم | للفصل بين الأجزاء
• استخدم , للفصل بين الخيارات
• رقم الإجابة يبدأ من 0
    """
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع للمعلم", callback_data="teacher_menu")],
        [InlineKeyboardButton("📋 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(msg, reply_markup=buttons)
    
    # حفظ حالة أن المستخدم يريد إضافة سؤال
    context.user_data['expecting_question'] = True

async def handle_teacher_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رسائل المعلم لإضافة الأسئلة"""
    if update.effective_user.id != TEACHER_ID:
        return
    
    if not context.user_data.get('expecting_question', False):
        return
    
    text = update.message.text.strip()
    
    try:
        # محاولة تحليل السؤال
        if "|" in text:
            parts = [p.strip() for p in text.split("|")]
            
            if len(parts) >= 3:  # سؤال صح/خطأ
                question, answer_str, explanation = parts[0], parts[1], parts[2]
                
                if answer_str.lower() in ['صح', 'صحيح', 'true', 'نعم']:
                    answer = True
                else:
                    answer = False
                
                q_id = db.add_true_false_question(question, answer, explanation)
                
                # رسالة النجاح
                success_msg = f"""
✅ **تم إضافة السؤال بنجاح!**

📝 **السؤال:** {question}
✅ **الإجابة:** {'صح' if answer else 'خطأ'}
📚 **رقم السؤال:** {q_id}
✨ **الشرح:** {explanation}

يمكنك إضافة المزيد من الأسئلة
                """
                
                # إبقاء حالة إضافة الأسئلة
                context.user_data['expecting_question'] = True
                
            elif len(parts) >= 4:  # سؤال اختيار
                question, options_str, answer_str, explanation = parts[0], parts[1], parts[2], parts[3]
                
                options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
                answer = int(answer_str.strip())
                
                q_id = db.add_mcq_question(question, options, answer, explanation)
                
                letters = ['أ', 'ب', 'ج', 'د', 'ه', 'و']
                correct_letter = letters[answer] if answer < len(letters) else str(answer)
                
                success_msg = f"""
✅ **تم إضافة السؤال بنجاح!**

📝 **السؤال:** {question}
✅ **الإجابة الصحيحة:** {correct_letter} ({options[answer]})
📚 **رقم السؤال:** {q_id}
✨ **الشرح:** {explanation}

يمكنك إضافة المزيد من الأسئلة
                """
                
                # إبقاء حالة إضافة الأسئلة
                context.user_data['expecting_question'] = True
                
            else:
                success_msg = "❌ **خطأ في التنسيق**\nاستخدم الشكل الصحيح كما في المثال"
        
        else:
            success_msg = "❌ **خطأ في التنسيق**\nاستخدم | لفصل أجزاء السؤال"
    
    except Exception as e:
        success_msg = f"❌ **حدث خطأ**\n{str(e)}\n\nجرب مرة أخرى باستخدام الشكل الصحيح"
    
    # إرسال رسالة النتيجة
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ أضف سؤالاً آخر", callback_data="teacher_add"),
            InlineKeyboardButton("📋 القائمة الرئيسية", callback_data="main_menu")
        ]
    ])
    
    await update.message.reply_text(success_msg, reply_markup=buttons)

async def teacher_view_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الأسئلة بطريقة منظمة"""
    query = update.callback_query
    await query.answer()
    
    tf_count = len(db.questions['true_false'])
    mcq_count = len(db.questions['mcq'])
    total = tf_count + mcq_count
    
    msg = f"""
📚 **مكتبة الأسئلة**

📊 **الإحصائيات:**
🔵 أسئلة صح/خطأ: {tf_count}
🔴 أسئلة اختيار: {mcq_count}
📋 الإجمالي: {total}

📝 **آخر 3 أسئلة صح/خطأ:**
"""
    
    # عرض آخر 3 أسئلة صح/خطأ
    for q in db.questions['true_false'][-3:]:
        answer = "✅ صح" if q['ans'] else "❌ خطأ"
        msg += f"\n🔹 {q['q'][:50]}... ({answer})"
    
    msg += "\n\n🔴 **آخر 3 أسئلة اختيار:**"
    
    # عرض آخر 3 أسئلة اختيار
    for q in db.questions['mcq'][-3:]:
        msg += f"\n🔸 {q['q'][:50]}..."
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ أضف سؤالاً", callback_data="teacher_add"),
            InlineKeyboardButton("📊 إحصائيات", callback_data="teacher_stats")
        ],
        [
            InlineKeyboardButton("🔙 رجوع", callback_data="teacher_menu")
        ]
    ])
    
    await query.edit_message_text(msg, reply_markup=buttons)

async def teacher_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات البوت"""
    query = update.callback_query
    await query.answer()
    
    total_students = len(db.data['students'])
    total_questions = db.data.get('total_questions', 0)
    correct_answers = db.data.get('correct_answers', 0)
    
    # حساب متوسط النجاح
    avg_success = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    msg = f"""
📈 **إحصائيات البوت**

👥 **الطلاب:**
• إجمالي الطلاب: {total_students}
• نشطين اليوم: {sum(1 for s in db.data['students'].values() if datetime.fromisoformat(s['last_active']).date() == datetime.now().date())}

📊 **الأسئلة:**
• إجمالي الأسئلة المجابة: {total_questions}
• الإجابات الصحيحة: {correct_answers}
• متوسط النجاح: {avg_success:.1f}%

🏆 **أفضل 3 طلاب:**
"""
    
    # ترتيب الطلاب حسب الإجابات الصحيحة
    sorted_students = sorted(
        db.data['students'].items(),
        key=lambda x: x[1].get('correct', 0),
        reverse=True
    )[:3]
    
    for i, (user_id, student) in enumerate(sorted_students):
        medal = ["🥇", "🥈", "🥉"][i]
        msg += f"\n{medal} {student['name']}: {student.get('correct', 0)} صحيح"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📚
