# واجهة ANCFCC Pro (ويب)

## هيكلة الملفات

| المسار | الغرض |
|--------|--------|
| `index.html` | هيكل الصفحة فقط — بدون منطق طويل |
| `css/main.css` | نقطة دخول الأنماط (ترتيب `@import` مهم) |
| `css/tokens.css` | ألوان، خطوط، ظلال — **تعديل المظهر العام هنا** |
| `css/base.css` | خلفية، ضوضاء، أورورا |
| `css/layout.css` | هيدر، بطل، شبكة البطاقات |
| `css/components.css` | أزرار، نوافذ، سجل، تقرير نواقص… |
| `css/stamp-modal.css` | مظهر نافذة معاينة الختم فقط |
| `css/tools/*.css` | **مظهر خاص بكل أداة** (شريط لون، إطار، عنوان) |
| `js/core.js` | سجل، حالة، انتظار، `eel.expose` |
| `js/engine.js` | مجلدات، `runCoreTool`, `runAdvanced`, ZIP |
| `js/missing.js` | تقرير النواقص، ختم جماعي، استرداد |
| `js/stamper.js` | معاينة الختم، سحب، أبعاد |
| `js/navigation.js` | `openToolPage`, `backToHome` |
| `js/sequential.js` | التشغيل التسلسلي |
| `js/init.js` | Tilt، إغلاق النوافذ بالنقر خارجها |

## قواعد التعديل

- **تغيير شكل أداة واحدة:** عدّل الملف تحت `css/tools/` المناسب (مثلاً `stamper.css`).
- **تغيير سلوك أداة:** عدّل الملف تحت `js/` المناسب دون المساس بـ CSS.
- **إضافة أداة جديدة:** أضف صفحة في `index.html` مع `class="tool-shell"` و `data-tool="اسم"`، ثم أنشئ `css/tools/اسم.css` وربطه من `css/main.css`.

## ترتيب تحميل السكربتات

`core` → `engine` → `missing` → `stamper` → `navigation` → `sequential` → `init`

لا تعيد ترتيبها دون مراجعة الاعتماديات (مثلاً `stamper` يستدعي `batchStampZn2` من `missing`).
