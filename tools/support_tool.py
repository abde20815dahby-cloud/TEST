from datetime import datetime


def run(engine, tool_key, options):
    ts = datetime.now().strftime("%H:%M:%S")
    if tool_key == "backup_open":
        res = engine.open_backup_folder()
        return {"ok": bool(res.get("ok")), "message": res.get("message", ""), "timestamp": ts}

    if tool_key == "undo":
        res = engine.undo()
        if res["ok"]:
            return {"ok": True, "message": f"تم التراجع عن: {res['message']}", "timestamp": ts}
        return {"ok": False, "message": res["message"], "timestamp": ts}

    if tool_key == "redo":
        res = engine.redo()
        if res["ok"]:
            return {"ok": True, "message": f"تمت إعادة: {res['message']}", "timestamp": ts}
        return {"ok": False, "message": res["message"], "timestamp": ts}

    if tool_key == "history_state":
        res = engine.history_state()
        return {
            "ok": True,
            "message": f"Undo: {res['undo_count']} | Redo: {res['redo_count']}",
            "timestamp": ts,
        }

    if tool_key == "zip_export":
        folder = options.get("folder")
        if not folder:
            return {"ok": False, "message": "حدد مجلد التصدير أولا.", "timestamp": ts}
        res = engine.export_zip_packages(folder)
        if not res.get("ok"):
            return {"ok": False, "message": res.get("message", "فشل التصدير"), "timestamp": ts}
        return {"ok": True, "message": f"تم إنشاء {res['count']} حزمة ZIP.", "timestamp": ts}

    if tool_key == "get_missing_report":
        data = getattr(engine, "global_missing_dict", None) or {}
        items = [{"folder": k, "missing": v} for k, v in data.items()]
        return {"ok": True, "report": items, "timestamp": ts}

    if tool_key == "copy_missing_numbers":
        data = getattr(engine, "global_missing_dict", None) or {}
        if not data:
            return {"ok": False, "message": "لا توجد أرقام لنسخها.", "text": "", "timestamp": ts}
        text = engine.missing_numbers(data)
        return {"ok": True, "message": "تم نسخ الأرقام.", "text": text, "timestamp": ts}

    if tool_key == "auto_distribute":
        folder = options.get("folder")
        if not folder:
            return {"ok": False, "message": "حدد مسار المخزن أولا.", "timestamp": ts}
        res = engine.auto_distribute_from_source(folder)
        return {"ok": res.get("ok", False), "message": res.get("message", ""), "timestamp": ts}

    if tool_key == "batch_stamp_zn2":
        # نفس معاملات insert_image لوحدة المصادقة ZN (x,y,w,h بالنقاط)
        res = engine.batch_stamp_missing_zn2(
            x=float(options.get("x", 20)),
            y=float(options.get("y", 20)),
            w=float(options.get("w", 150)),
            h=float(options.get("h", 80)),
        )
        return {"ok": res.get("ok", False), "message": res.get("message", ""), "timestamp": ts}

    if tool_key == "manual_insert":
        target = options.get("target_folder")
        source = options.get("source_file")
        missing_name = options.get("missing_file_name", "zn2.pdf")
        if not target or not source:
            return {"ok": False, "message": "حدد المجلد والملف المصدر.", "timestamp": ts}
        res = engine.manual_insert_missing(target, source, missing_name)
        return {"ok": res.get("ok", False), "message": res.get("message", ""), "timestamp": ts}

    return {"ok": False, "message": "أداة دعم غير معروفة.", "timestamp": ts}
