# 7-Day Trend Analysis

## Purpose
Analyze trends for key ICU parameters over 7 days.

## Input
Array of structured JSON data for past 7 days

## Output
Turkish markdown report with:

```markdown
# 7 Günlük Trend Analizi

## Vazopresör İhtiyacı
[ASCII graph or table showing daily vasopressor doses]
**Trend:** ↓ Azalıyor / ↑ Artıyor / → Stabil
**Yorum:** [interpretation]

## Laktat Düzeyleri
[Trend visualization]
**Trend:** [direction]
**Yorum:** [interpretation]

## Böbrek Fonksiyonu (Kreatinin)
[Trend visualization]
**Trend:** [direction]
**Yorum:** [interpretation]

## Enfeksiyon Belirteçleri (WBC, CRP, PCT)
[Trends]
**Yorum:** [interpretation]

## Solunum Durumu (FiO2, PEEP)
[Trends]
**Yorum:** [interpretation]

## Genel Değerlendirme
[Overall trajectory assessment]

## Öneriler
- [Recommendation based on trends]
```

## Key Parameters to Track
- Vasopressor dose (trend direction)
- Lactate (clearing or worsening)
- Creatinine (AKI improvement/worsening)
- WBC, CRP, PCT (infection response)
- FiO2, PEEP, P/F ratio (respiratory trend)
- Urine output (renal recovery)
- GCS (neurological recovery)

## Trend Visualization
Use ASCII tables or simple text graphs.

Example:
```
Gün:  1    2    3    4    5    6    7
NE:  0.3  0.25 0.2  0.18 0.15 0.15 0.15
Lak: 3.2  2.8  2.1  1.8  1.6  1.5  1.4
```

Provide clear interpretation in Turkish.
