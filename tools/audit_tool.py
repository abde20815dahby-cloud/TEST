from datetime import datetime


def run(engine, tool_key):
    ts = datetime.now().strftime("%H:%M:%S")
    if not engine.project_root:
        return {
            "ok": False,
            "tool": tool_key,
            "message": "حدد مسار المشروع أولا قبل تشغيل الأدوات.",
            "timestamp": ts,
        }

    if tool_key == "cleaning":
        res = engine.clean_extras()
        msg = (
            f"تم التطهير: نقل {res['moved_count']} عنصر غير معتمد "
            f"بعد فحص {res['folders_scanned']} مجلد."
        )
        return {"ok": True, "tool": "التطهير الذكي", "message": msg, "timestamp": ts}

    if tool_key == "missing_check":
        missing = engine.check_missing()
        engine.global_missing_dict = dict(missing)
        if not missing:
            msg = "لا توجد نواقص. كل الملفات المرجعية متوفرة ومتطابقة."
            return {"ok": True, "tool": "فحص النواقص", "message": msg, "timestamp": ts, "has_missing": False}
        numbers = engine.missing_numbers(missing)
        msg = f"تم اكتشاف نواقص في {len(missing)} مجلد. الأرقام: [{numbers or 'غير متاحة'}]"
        return {
            "ok": False,
            "tool": "فحص النواقص",
            "message": msg,
            "timestamp": ts,
            "has_missing": True,
            "missing_count": len(missing),
        }

    if tool_key == "auto_validation":
        clean_res = engine.clean_extras()
        missing = engine.check_missing()
        engine.global_missing_dict = dict(missing)
        if not missing:
            msg = (
                f"اكتملت المصادقة الآلية: تطهير {clean_res['moved_count']} عنصر "
                "ولا توجد نواقص."
            )
            return {"ok": True, "tool": "المصادقة الآلية", "message": msg, "timestamp": ts}
        numbers = engine.missing_numbers(missing)
        msg = (
            f"اكتملت خطوة التطهير ({clean_res['moved_count']} عنصر)، "
            f"لكن ما زالت نواقص في {len(missing)} مجلد: [{numbers or 'غير متاحة'}]."
        )
        return {"ok": False, "tool": "المصادقة الآلية", "message": msg, "timestamp": ts, "has_missing": True}

    return {"ok": False, "tool": tool_key, "message": "أداة غير معروفة.", "timestamp": ts}
