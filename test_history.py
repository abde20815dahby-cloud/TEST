# مسار الملف: test_history.py (في المجلد الرئيسي)
import os
from core.history import ActionHistoryManager

def run_test():
    print("🚀 Démarrage du test unitaire (Unit Test)...\n")
    
    history = ActionHistoryManager()
    # درنا مسار مطلق (Chemin absolu) باش نتفاداو أي مشكل مع الويندوز
    test_file = os.path.abspath("test_document.txt")
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("محتوى أصلي: هذا محضر تحديد قبل التعديل.")
    print(f"✅ تم إنشاء الملف: {test_file}")
    
    history.start_batch("تعديل محضر التحديد")
    history.record_before(test_file)
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("محتوى معدل: تمت إضافة ختم المهندس بنجاح.")
        
    history.record_after(test_file)
    history.commit_batch()
    print("✅ تم تعديل الملف وحفظ العملية في السجل.")
    
    with open(test_file, "r", encoding="utf-8") as f:
        print(f"📝 المحتوى الحالي: {f.read()}\n")
        
    print("🔄 جاري التراجع (Undo)...")
    success, msg = history.undo()
    with open(test_file, "r", encoding="utf-8") as f:
        print(f"📝 المحتوى بعد التراجع: {f.read()}\n")
        
    print("↪️ جاري الإعادة (Redo)...")
    success, msg = history.redo()
    with open(test_file, "r", encoding="utf-8") as f:
        print(f"📝 المحتوى بعد الإعادة: {f.read()}\n")
        
    if os.path.exists(test_file):
        os.remove(test_file)
    print("🎉 انتهى الاختبار بنجاح (Test réussi)!")

if __name__ == "__main__":
    run_test()