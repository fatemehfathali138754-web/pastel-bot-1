import os, json, threading, asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

class H(BaseHTTPRequestHandler):
    def do_GET(s): s.send_response(200); s.end_headers(); s.wfile.write(b"OK")
    def do_HEAD(s): s.send_response(200); s.end_headers()

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever(), daemon=True).start()

TOKEN = "8816292939:AAEN-e8TRuyQOWBHQGdBsPcl4_rHKD8Q7Mk"
ADMIN = 8489885798
DB = "booklets_1.json"
CH = [
    {"id": "@PastelFinal", "t": "📢 کانال اول", "u": "https://t.me/PastelFinal"},
    {"id": "@VlP_KLID", "t": "📢 کانال دوم", "u": "https://t.me/VlP_KLID"},
    {"id": -1004361916345, "t": "👥 گروه", "u": "https://t.me/+2gHubFEar48yODZk"}
]

def db_rw(w=None):
    if w is not None: json.dump(w, open(DB, "w", encoding="utf-8"), ensure_ascii=False)
    try: return json.load(open(DB, "r", encoding="utf-8")) if os.path.exists(DB) else []
    except: return []

async def is_sub(u, b):
    for c in CH:
        try:
            m = await b.get_chat_member(c["id"], u)
            if m.status not in ["member", "administrator", "creator"]: return False
        except: return False
    return True

def l_kb(): return IKM([[IKB(f"📚 {x['name']}", callback_data=f"dl_{i}")] for i, x in enumerate(db_rw())])
def d_kb(): return IKM([[IKB(f"❌ حذف: {x['name']}", callback_data=f"rm_{i}")] for i, x in enumerate(db_rw())])

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if await is_sub(u.effective_user.id, c.bot):
        b = db_rw()
        await u.message.reply_text("جزوه مورد نظر را انتخاب کنید:" if b else "✅ تایید شد. جزوه‌ای نیست.", reply_markup=l_kb() if b else None)
    else:
        await u.message.reply_text("برای دانلود در کانال‌ها عضو شوید:", reply_markup=IKM([[IKB(x["t"], url=x["u"])] for x in CH] + [[IKB("✅ عضو شدم", callback_data="chk")]]))

async def del_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == ADMIN:
        b = db_rw()
        await u.message.reply_text("انتخاب جزوه برای حذف:" if b else "لیست خالی است.", reply_markup=d_kb() if b else None)

async def cb(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    if q.data.startswith("rm_") and q.from_user.id == ADMIN:
        b = db_rw(); idx = int(q.data[3:])
        if idx < len(b): b.pop(idx); db_rw(b)
        await q.edit_message_reply_markup(reply_markup=d_kb() if b else None)
    elif not await is_sub(q.from_user.id, c.bot):
        await q.answer("❌ عضو نشدید!", show_alert=True)
    elif q.data == "chk":
        b = db_rw()
        await q.edit_message_text("جزوه مورد نظر را انتخاب کنید:" if b else "✅ تایید شد. جزوه‌ای نیست.", reply_markup=l_kb() if b else None)
    elif q.data.startswith("dl_"):
        b = db_rw(); i = int(q.data[3:])
        if i < len(b): await c.bot.send_document(q.from_user.id, b[i]["id"], caption=f"📚 {b[i]['name']}\n\n@PastelFinal")

async def doc(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == ADMIN:
        d = u.message.document
        b = db_rw(); b.append({"name": (d.file_name or "جزوه").replace(".pdf",""), "id": d.file_id}); db_rw(b)
        await u.message.reply_text("✅ اضافه شد.", reply_markup=l_kb())

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

app = ApplicationBuilder().token(TOKEN).build()
for h in [CommandHandler("start", start), CommandHandler("del", del_cmd), CallbackQueryHandler(cb), MessageHandler(filters.Document.ALL, doc)]: app.add_handler(h)
app.run_polling(drop_pending_updates=True)
