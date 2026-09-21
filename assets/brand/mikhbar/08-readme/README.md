# Mikhbar Brand Assets Pack

حزمة الهوية الرسمية لمنصة **Mikhbar / مِخبار**، مبنية مباشرة من الملفات المرجعية المرفقة: رمز الشعار، الشعار الكتابي، الأيقونة، وفيديو الحركة.

## الاستخدام السريع للموقع
- للهيدر: `06-web-ready/header-logo/mikhbar-header-logo-transparent.png`
- للهيدر بصيغة SVG حافظة للعمل الأصلي: `06-web-ready/header-logo/mikhbar-header-logo.svg`
- للفافيكون: `06-web-ready/favicon/favicon.ico`
- Apple Touch Icon: `06-web-ready/favicon/apple-touch-icon.png`
- Android/PWA: `android-chrome-192x192.png` و `android-chrome-512x512.png`
- حركة الرمز الشفافة للويب: `06-web-ready/lightweight-animations/mikhbar-logo-mark-alpha.webm`
- بديل كصورة متحركة شفافة: `mikhbar-logo-mark-alpha.webp`
- حركة الشعار الكامل الشفافة: `mikhbar-full-logo-alpha.webm`
- MP4 بخلفية بيضاء كبديل عام: الملفات التي تنتهي بـ `fallback-white.mp4`

## المجلدات
- `01-logo-mark`: رمز Mikhbar وحده، شفاف/أبيض/أحادي اللون/SVG.
- `02-full-logo`: الشعار الكامل Mikhbar، شفاف/أبيض/أحادي اللون/SVG.
- `03-icon`: الأيقونة والفافيكون بكل المقاسات الأساسية.
- `04-animated-logo-mark`: حركة الرمز وحده.
- `05-animated-full-logo`: حركة الشعار الكامل.
- `06-web-ready`: الملفات الجاهزة مباشرة للموقع.
- `07-preview`: لوحة معاينة للهوية.
- `00-sources`: الملفات الأصلية المرجعية.

## صيغ الحركة الشفافة
- **WEBM VP9 Alpha**: النسخة الموصى بها للاستخدام المباشر في الويب عند الحاجة إلى خلفية شفافة.
- **MOV ProRes 4444**: نسخة Master عالية الجودة للتحرير والمونتاج، وتحمل Alpha حقيقي.
- **Animated WebP**: بديل خفيف نسبيًا للاستخدام كصورة متحركة شفافة.
- **APNG**: نسخة شفافة عالية الجودة للرمز، لكنها أكبر حجمًا.

## ملفات الخلفية البيضاء
- **MP4/H.264**: أفضل توافق عام.
- **WebM**: بديل ويب مضغوط.
- **GIF**: للتوافق عند الحاجة فقط، لأنه أقل كفاءة من WebP/WebM.

## ملاحظة SVG
ملفات SVG الملونة المسماة `preserved-artwork.svg` تحفظ العمل البصري الأصلي داخل حاوية SVG بدون إعادة رسم الهوية أو تشويه التدرجات؛ لذلك هي ليست إعادة رسم Vector كاملة. أما ملفات `monochrome-vector.svg` فهي Silhouette متجهة فعلًا للاستخدام الأحادي اللون.

## الألوان
راجع `08-readme/brand-colors.txt` و `06-web-ready/mikhbar-brand.css`.

## نصيحة أداء
لأسرع تحميل للموقع، ابدأ بـ WEBM الشفاف أو Animated WebP، واستخدم PNG ثابت كـ poster/fallback. لا تستخدم GIF كخيار أول لأنه أثقل عادةً لنفس الجودة.
