# PAI‑6 Sovereign — v3.2.3 (Rebuild) — RUNBOOK

## نظرة عامة
هذه الحزمة تشغّل Backend FastAPI + واجهة Dashboard + Docker + زر ذهبي للنشر على Cloud Run + Self‑Healing Monitor.

## تشغيل محلي (بدون Docker)
1) Python 3.11
2) `pip install -r backend/requirements.txt`
3) `uvicorn app.main:app --host 0.0.0.0 --port 8080` من داخل مجلّد `backend`
4) افتح: `http://localhost:8080/` أو `/dashboard/`

## تشغيل بـ Docker
```
docker compose -f ops/docker-compose.yml up --build
```
افتح `http://localhost:8080/`

## النشر عبر الزر الذهبي (Cloud Shell — أسهل طريقة)
- افتح Google Cloud Shell (حسابك مفعّل + Billing مفعّل).
- نفّذ:
```
bash scripts/golden.sh "<PUBLIC_ZIP_URL>" "pai6-sovereign" "me-central2"
```
حيث `<PUBLIC_ZIP_URL>` هو رابط عام للحزمة zip (مثلاً من Google Drive بوضع Anyone with the link).  
السكربت سيفك الضغط ويبني الصورة وينشر الخدمة ويطبع لك رابط HTTPS النهائي.

### نشر من مجلد المصدر مباشرة (بدون رابط)
ارفع ملفات الحزمة إلى Cloud Shell (Upload)، ثم:
```
bash scripts/golden.sh "" "pai6-sovereign" "me-central2"
```

## Self‑Healing
- سكربت `self_healing/self_heal.sh` يفحص `/api/system/healthz` ويعيد نشر نفس الصورة إن فشل الفحص.
- يمكن جدولته عبر Cloud Scheduler أو تشغيله يدويًا.

## الأمن والحوكمة (مختصر)
- فعّل Cloud Armor/Rate Limiting حسب خطتك.
- استخدم API keys/ID Tokens وراء API Gateway إن لزم.
- حدّث CORS في `main.py` للإنتاج.
