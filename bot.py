import os, json, threading, asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton as B, InlineKeyboardMarkup as M
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

class H(BaseHTTPRequestHandler):
    do_GET = lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"OK"))
    do_HEAD = lambda s: (s.send_response(200), s.end_headers())
threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.getenv("PORT", 10000))), H).serve_forever(), daemon=True).start()

ADM = 8489885798
CHS = [
    ("@PastelFinal", "📢 کانال اول", "https://t.me/PastelFinal"),
    ("@VlP_KLID", "📢 کانال دوم", "https://t.me/VlP_KLID"),
    (-1004361916345, "👥 گروه", "https://t.me/+2gHubFEar48yODZk")
]

async def is_sub(uid, bot):
    for cid, _, _ in CHS:
        try:
            m = await bot.get_chat_member(cid, uid)
            if m.status not in ["member", "administrator", "creator"]: return False
        except: return False
    return True

def make_app(tok, db):
    def rw(w=None):
        if w is not None:
            with open(db, "w", encoding="utf-8") as f: json.dump(w, f, ensure_ascii=False)
        return json.load(open(db, "r", encoding="utf-8")) if os.path.exists(db) else []

    kb_dl = lambda: M([[B(f"📚 {x['name']}", callback_data=f"dl_{i}")] for i, x in enumerate(rw())])
    kb_rm = lambda: M([[B(f"❌ حذف: {x['name']}", callback_data=f"rm_{i}")] for i, x in enumerate(rw())])

    async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
        if await is_sub(u.effective_user.id, c.bot):
            d = rw(); await u.message.reply_text("جزوه مورد نظر را انتخاب کنید:" if d else "✅ تایید شد. جزوه‌ای نیست.", reply_markup=kb_dl() if d else None)
        else:
            await u.message.reply_text("برای دانلود در کانال‌ها عضو شوید:", reply_markup=M([[B(t, url=l)] for _, t, l in CHS] + [[B("✅ عضو شدم", callback_data="chk")]]))

    async def del_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
        if u.effective_user.id == ADM:
            d = rw(); await u.message.reply_text("انتخاب جزوه برای حذف:" if d else "لیست خالی است.", reply_markup=kb_rm() if d else None)

    async def cb(u: Update, c: ContextTypes.DEFAULT_TYPE):
        q = u.callback_query; await q.answer(); uid = q.from_user.id
        if q.data.startswith("rm_") and uid == ADM:
            d = rw(); d.pop(int(q.data[3:])); rw(d); await q.edit_message_reply_markup(reply_markup=kb_rm() if d else None)
        elif not await is_sub(uid, c.bot): await q.answer("❌ عضو نشدید!", show_alert=True)
        elif q.data == "chk":
            d = rw(); await q.edit_message_text("جزوه مورد نظر را انتخاب کنید:" if d else "✅ تایید شد. جزوه‌ای نیست.", reply_markup=kb_dl() if d else None)
        elif q.data.startswith("dl_"):
            d = rw(); i = int(q.data[3:])
            if i < len(d): await c.bot.send_document(uid, d[i]["id"], caption=f"📚 {d[i]['name']}\n\n@PastelFinal")

    async def doc(u: Update, c: ContextTypes.DEFAULT_TYPE):
        if u.effective_user.id == ADM:
            d = u.message.document; data = rw()
            data.append({"name": (d.file_name or "جزوه").replace(".pdf", ""), "id": d.file_id})
            rw(data); await u.message.reply_text("✅ اضافه شد.", reply_markup=kb_dl())

    a = ApplicationBuilder().token(tok).build()
    for h in [CommandHandler("start", start), CommandHandler("del", del_cmd), CallbackQueryHandler(cb), MessageHandler(filters.Document.ALL, doc)]:
        a.add_handler(h)
    return a

a1 = make_app("8816292939:AAEN-e8TRuyQOWBHQGdBsPcl4_rHKD8Q7Mk", "booklets_1.json")
a2 = make_app("8864428476:AAGvMDDQqcX5zYbvEA0iLkI5VW1SVkXGogI", "booklets_2.json")

async def main():
    await a1.initialize(); await a2.initialize()
    await a1.start(); await a2.start()
    await a1.updater.start_polling(drop_pending_updates=True)
    await a2.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if name == "main":
    asyncio.run(main())
