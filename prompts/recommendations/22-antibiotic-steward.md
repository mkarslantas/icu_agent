# Antibiyotik Yönetimi ve Stewardship Önerileri

## Amaç
Enfeksiyon verileri ve kültür sonuçlarını değerlendirerek antibiyotik stewardship prensipleri doğrultusunda öneriler sunmak.

## Giriş Verileri
- Enfeksiyon kaynağı ve tanısı
- Mevcut antibiyotik tedavisi (ilaç, doz, gün)
- Kültür sonuçları ve antibiyogram
- Enflamatuar belirteçler (WBC, CRP, PCT)
- Klinik yanıt (ateş, hemodinamik, organ fonksiyonları)

## Referans
`config/antibiotic-guidelines.yaml` - Detaylı antibiyotik protokolleri

## Çıktı Formatı
Türkçe markdown raporu:

```markdown
# 💊 ANTİBİYOTİK YÖNETİMİ VE STEWARDSHIP ÖNERİLERİ

## Enfeksiyon Özeti
**Tanı:** [diagnosis]
**Kaynak:** [source]
**Enfeksiyon Günü:** [day]
**Şiddet:** [Sepsis / Septik şok / Lokal enfeksiyon]

## Mevcut Antibiyotik Tedavisi
**İlaç(lar):** [antibiotic name(s)]
**Doz/Sıklık:** [dose and frequency]
**Rota:** [IV/PO]
**Tedavi Günü:** [current day]
**Endikasyon:** [empirik / kültür yönlendirilmiş]

## Klinik Yanıt Değerlendirmesi

### Klinik Parametreler
- **Ateş:** [value]°C (Trend: ↓/↑/→)
- **Hemodinamik:** [stable/unstable, vasopressor requirement]
- **WBC:** [value] K/µL (Trend: ↓/↑/→)
- **CRP:** [value] mg/L (Trend: ↓/↑/→)
- **PCT:** [value] ng/mL (Trend: ↓/↑/→)

### Yanıt Değerlendirmesi
[✓ İyi Klinik Yanıt / ⚠️ Kısmi Yanıt / ❌ Yanıtsız]

**Değerlendirme:**
[Ateş normalleşiyor mu, WBC düşüyor mu, PCT azalıyor mu, hemodinamik stabilite, organ fonksiyonları]

## Mikrobiyoloji

### Kültür Sonuçları
**[Kültür Tipi]:** [Date]
- **Sonuç:** [Positive/Negative/Pending]
- **Organizma:** [organism name or "üreme yok"]
- **Duyarlılık:** [antibiyogram results]

### Antibiyogram Analizi
**Mevcut antibiyotiğe duyarlılık:** [Duyarlı / Dirençli / Orta / Bilinmiyor]

[Eğer organizma ürediyse duyarlılık listesi]

## Stewardship Önerileri

### Öncelik 1: [DE-ESCALATION / DEVAM / ESCALATION / DURDUR]

#### A. De-Escalation (Spektrum Daraltma) ✅ ÖNERİLİR
[Eğer kültür sonucu var ve duyarlılık bellidir]

**Gerekçe:**
- Kültür sonucu mevcut ve duyarlılık belli
- Klinik yanıt iyi
- Geniş spektrumdan dar spektruma geçilebilir

**Spesifik Öneri:**
[Mevcut antibiyotik] → [Dar spektrumlu antibiyotik]

**Örnek:**
"Meropenem → Ceftriaxone geçiş yapılabilir (E. coli ESBL negatif, 3. kuşak sefalosporinlere duyarlı)"

**Avantajlar:**
- Kollateral hasar azalır (C. diff riski, direnç gelişimi)
- Maliyet azalır
- Aynı etkinlik korunur

#### B. Devam ✅ / Duration Belirleme
[Eğer tedavi devam etmeli ama süre belirlenmelidir]

**Tedavi Süresi Önerisi:**
**Toplam Süre:** [X gün] (Kalan: [Y gün])

**Gerekçe:**
- [Enfeksiyon tipi için kanıta dayalı süre]

**Enfeksiyon Tipine Göre Süreler:**
- **Pnömoni (HAP/VAP):** 7 gün (standart), 14 gün (non-fermenter veya kavitasyon)
- **Bakteremi (Gram-):** 7-14 gün (kaynağa bağlı)
- **Bakteremi (S. aureus):** 14 gün minimum (komplikasyonsuz), 4-6 hafta (komplikeli)
- **İntra-abdominal:** 4-7 gün (kaynak kontrolü sonrası)
- **Üriner (pyelonephritis/urosepsis):** 7-14 gün

**Durdurma Kriterleri:**
- [X]. günde PCT <0.5 ng/mL veya %80 azalma
- Ateş yok >48 saat
- Hemodinamik stabil, vazopresör yok
- WBC normalize

**Tekrar Değerlendirme:** [X]. günde re-evaluate

#### C. Escalation (Genişletme) ⚠️
[Eğer klinik yanıt yetersiz veya dirençli organizma]

**İndikasyon:**
- Klinik kötüleşme devam ediyor
- Mevcut antibiyotik dirençli bulundu
- Yeni enfeksiyon odağı gelişti

**Öneri:**
[Mevcut] + [İlave antibiyotik] veya [Daha geniş spektrumlu antibiyotik]

**Örnek:**
"MRSA izolatı için Vancomycin eklenmeli (hedef trough 15-20 mcg/mL)"

#### D. Durdurma ⛔
[Eğer enfeksiyon dışlanmışsa]

**Gerekçe:**
- Kültürler negatif (48-72 saat)
- Alternatif tanı bulundu
- Klinik olarak enfeksiyon kanıtı yok

**Öneri:**
Antibiyotik [X]. günde DURDUR

**Takip:**
- Klinik izlem devam
- Gerekirse tekrar başlanabilir

## Dozlama Optimizasyonu

### Farmakokinetik/Farmakodinamik Optimizasyon
[Eğer uygulanabilirse]

**Extended İnfüzyon Beta-Laktamlar:**
- Piperacillin-Tazobactam 4.5g over 4 hours q8h
- Meropenem 1-2g over 3 hours q8h
**Gerekçe:** Time-dependent killing, yüksek MIC izolatlarında etkinlik artışı

**Vankomisin Loading Dose:**
- 25-30 mg/kg IV loading (ağır enfeksiyon)
- Hedef trough: 15-20 mcg/mL (ciddi MRSA enfeksiyonları)

### Böbrek Fonksiyonuna Göre Doz Ayarı
**Kreatinin:** [value] mg/dL
**GFR (tahmini):** [value] mL/dk

[Eğer böbrek yetmezliği varsa doz önerisi]

## Kaynak Kontrolü

**Kaynak kontrolü:** [✓ Sağlandı / ❌ Gerekli ama yapılmadı / ⚠️ Değerlendirilmeli]

**Öneri:**
[Eğer kaynak kontrolü yetersizse: drenaj, debridman, kateter çıkarma vb.]

**Uyarı:** Kaynak kontrolü olmadan antibiyotik başarısız olabilir!

## Yan Etki ve Komplikasyon İzlemi

### Monitörizasyon
- **Vankomisin:** Böbrek fonksiyonu, trough düzeyleri
- **Linezolid:** Tam kan sayımı (trombositopeni), >14 gün tedavide nöropati
- **Aminoglikozid:** Böbrek fonksiyonu, işitme (ototoksisite)
- **Fluorokinolon:** QT uzaması (EKG), tendon rüptürü riski

### C. difficile Riski
**Risk faktörleri:** Geniş spektrum antibiyotik, uzun süre, yaşlılık, PPI kullanımı
**Öneri:** Mümkün olduğunca dar spektrum, kısa süre

## Kombine Tedavi

### Pseudomonas için Çift Tedavi
**İndikasyon:** Ağır enfeksiyon, septik şok, nötropeni
**Öneri:** Beta-laktam + aminoglikozid veya fluorokinolon
**Süre:** Çift tedavi 5-7 gün, sonra monoterapi

## Profilaktik Tedavi

[Eğer profilaksi değerlendiriliyorsa]
- SDD (Selective Digestive Decontamination): [Endikasyon değerlendirmesi]
- Antifungal profilaksi: [Yüksek riskli hasta değerlendirmesi]

## Kanıt Temeli
- **Surviving Sepsis Campaign 2021:** Erken uygun antibiyotik (<1 saat), de-escalation
- **IDSA Guidelines:** Enfeksiyona özel tedavi süreleri
- **PCT-guided therapy:** Solunum enfeksiyonlarında süre kısaltabilir

## Özet Öneri
**[1-2 cümlelik açık, uygulanabilir öneri]**

**Örnekler:**
- "E. coli ESBL negatif, Ceftriaxone'a duyarlı. Meropenem → Ceftriaxone 2g q24h de-escalation yapılabilir. Toplam 7 gün tedavi önerilir (kalan 2 gün)."
- "Kültürler 72 saatte negatif, PCT 0.3 ng/mL'ye düştü, klinik düzelme mevcut. Antibiyotik bugün durdurulabilir, klinik izlem devam."
- "MRSA bakteremisi devam ediyor, Vancomycin trough düşük (8 mcg/mL). Doz artırılmalı, hedef trough 15-20 mcg/mL. Minimum 14 gün tedavi (ilk negatif kültürden itibaren)."

---
*Antibiyotik kararları hasta bazında, klinik yanıt ve mikrobiyoloji sonuçları ile birlikte değerlendirilmelidir.*
```

## Stewardship Prensipleri
1. **Right Drug:** En spesifik, en dar spektrumlu etkili antibiyotik
2. **Right Dose:** Farmakokinetik/farmakodinamik optimizasyon
3. **Right Duration:** Kanıta dayalı en kısa etkili süre
4. **De-escalation:** 48-72 saat içinde kültüre göre daraltma
5. **Source Control:** Antibiyotik tek başına yeterli değil
6. **Monitoring:** Etkinlik, toksisite, direnç izlemi
7. **Stop:** Enfeksiyon yoksa veya tedavi süresi tamamsa DURDUR

Tüm öneriler Türkçe, spesifik, kanıta dayalı ve uygulanabilir olmalıdır.
