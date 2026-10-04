"""Формирует dictionary_rows.tex — строки словаря переменных; числа берутся из кода practice.ipynb."""
import json
import re

import matplotlib

matplotlib.use("Agg")

ns = {"display": lambda *a, **k: None}
for cell in json.load(open("practice.ipynb"))["cells"]:
    if cell["cell_type"] == "code":
        exec("".join(cell["source"]), ns)

df, cohort, kept, replaced_by, duplicates, absorbed, root = (
    ns[k] for k in ("df", "cohort", "kept", "replaced_by", "duplicates", "absorbed", "root"))
N_ALL, N_COH = len(df), len(cohort)


def tt(name):
    """Имя переменной моноширинным шрифтом с возможностью переноса после «_» и на границах CamelCase."""
    s = name.replace("#", r"\#").replace("_", r"\_\allowbreak{}")
    if name.startswith("GTVp_"):
        s = re.sub(r"(?<=[a-z])(?=[A-Z])", r"\\allowbreak{}", s)
    return r"\texttt{" + s + "}"


def miss(c):
    a, b = int(df[c].isna().sum()), int(cohort[c].isna().sum())
    fa = f"{a} ({df[c].isna().mean() * 100:.1f}~\\%)".replace(".", ",") if a else "0"
    fb = f"{b} ({cohort[c].isna().mean() * 100:.1f}~\\%)".replace(".", ",") if b else "0"
    return f"{fa} / {fb}"


PRE = "до начала лечения, при постановке диагноза"
STAGING = "до начала лечения, после стадирования"
PLAN = "до начала ЛТ, при утверждении плана лечения"
CT = "до начала лечения, по диагностической КТ"

clinical = [
    ("Patient_ID", "код пациента, присвоенный при анонимизации; совпадает с именем папки снимков",
     "целый, 1–315, уникален", "служебная, всегда",
     "оставить как ключ строки; не признак: идентификатор не несёт клинической информации"),
    ("Fold", "часть набора соревнования", "категориальный: Training, Test",
     "служебная, задана организаторами",
     "исключить: служебная переменная; после исключения Test — константа (Training)"),
    ("Local_tumor_recurrence", "локальный рецидив первичной опухоли за период наблюдения",
     "бинарный: 0, 1; в Test пусто", "после наблюдения не менее 2 лет",
     "исключить из признаков: источник целевой переменной; 158 пустых значений Test — неопределённый исход"),
    ("Gender", "пол", "категориальный: Male, Female", PRE, "оставить"),
    ("Age_at_diagnosis", "возраст на момент диагноза, лет", "целый, 30–89", PRE,
     "оставить; при сокращении избыточности не заменяет других"),
    ("Race", "раса", "категориальный: White, Black, Hispanic, Asian, American\\_Indian/\\allowbreak{}Alaska\\_Native", PRE,
     "оставить; пустая ячейка — пропуск, не заполнять"),
    ("Tumor_side", "латеральность опухоли", "категориальный: L, R, Bilateral", STAGING, "оставить"),
    ("Tumor_subsite", "подобласть ротоглотки", "категориальный: BOT, Tonsil, GPS, Soft\\_palate, Pharyngeal\\_wall, Other",
     STAGING, "оставить"),
    ("T_category", "категория T (AJCC 7)", "порядковый: 1–4", STAGING, "оставить"),
    ("N_category", "категория N (AJCC 7)", "порядковый: 0, 1, 2a, 2b, 2c, 3", STAGING,
     "оставить; служебный код X (1 значение) заменён пропуском"),
    ("AJCC_Stage", "стадия по AJCC 7, определяется T и N при M0", "порядковый: I–IV", STAGING,
     "оставить; X (1) заменён пропуском, III при T4N1 (1) исправлено на IV"),
    ("Pathological_grade", "степень дифференцировки опухоли", "порядковый: I, I-II, II, II-III, III, IV",
     "до начала лечения, по биопсии", "оставить; пропуски не заполнять, доля ниже порога 30~\\%"),
    ("Smoking_status_at_diagnosis", "статус курения на момент диагноза", "категориальный: Never, Former, Current",
     PRE, "оставить"),
    ("Smoking_Pack-Years", "кумулятивное курение, пачко-лет", "непрерывный, $\\geq 0$; 0 только при Never", PRE,
     "оставить; 7 нулей при Current/Former заменены пропуском; при сокращении не заменяет других"),
    ("Radiation_treatment_course_duration", "фактическая длительность курса ЛТ, дни", "целый, 32–56",
     "после окончания ЛТ", "исключить: неизвестна в момент применения модели"),
    ("Total_prescribed_Radiation_treatment_dose", "суммарная предписанная доза, Гр", "целый: 60, 63, 66, 70, 72", PLAN,
     "оставить; при сокращении не заменяет других"),
    ("#_Radiation_treatment_fractions", "число фракций", "целый, 30–40", PLAN,
     "исключить: избыточна, $|\\rho| > 0{,}9$ с Dose\\_per\\_fraction"),
    ("Induction_Chemotherapy", "индукционная химиотерапия до ЛТ", "бинарный: Y, N", PLAN, "оставить"),
    ("Concurrent_chemotherapy", "химиотерапия одновременно с ЛТ", "бинарный: Y, N", PLAN, "оставить"),
    ("KM_Overall_survival_censor", "жизненный статус на последнем наблюдении", "бинарный: 1 — жив, 0 — умер",
     "после наблюдения", "исключить: неизвестна в момент применения модели, отражает исход лечения"),
    ("Dose_per_fraction", "вычисленная: доза на фракцию, Гр (доза / число фракций)", "непрерывный, 1,8–2,4", PLAN,
     "оставить; заменяет 1 исключённый: \\#\\_Radiation\\_treatment\\_fractions"),
    ("Target_local_recurrence", "целевая: 1 — локальный рецидив, 0 — нет",
     "бинарный: 0 (128), 1 (12)", "после наблюдения не менее 2 лет",
     "целевая переменная; 158 пациентов с неопределённым исходом исключены, нулём не кодировались"),
]

radiomic_meaning = {
    "shape_MeshVolume": ("объём опухоли по треугольной сетке", "непрерывный, мм$^3$, $>0$"),
    "shape_Sphericity": ("сферичность", "непрерывный, (0; 1]"),
    "shape_Elongation": ("вытянутость: отношение второй главной оси к первой", "непрерывный, (0; 1]"),
    "shape_Flatness": ("уплощённость: отношение третьей главной оси к первой", "непрерывный, (0; 1]"),
    "shape_MajorAxisLength": ("длина наибольшей главной оси", "непрерывный, мм, $>0$"),
    "shape_Maximum2DDiameterSlice": ("наибольший диаметр в аксиальной плоскости", "непрерывный, мм, $>0$"),
    "shape_SurfaceVolumeRatio": ("отношение площади поверхности к объёму", "непрерывный, мм$^{-1}$, $>0$"),
    "firstorder_10Percentile": ("10-й перцентиль плотности", "непрерывный, HU"),
    "firstorder_90Percentile": ("90-й перцентиль плотности", "непрерывный, HU"),
    "firstorder_Entropy": ("энтропия гистограммы плотностей", "непрерывный, бит, $\\geq 0$"),
    "firstorder_Kurtosis": ("эксцесс распределения плотностей", "непрерывный, $\\geq 1$"),
    "firstorder_Maximum": ("максимальная плотность", "непрерывный, HU"),
    "firstorder_Mean": ("средняя плотность", "непрерывный, HU"),
    "firstorder_Median": ("медиана плотности", "непрерывный, HU"),
    "firstorder_Minimum": ("минимальная плотность", "непрерывный, HU"),
    "firstorder_RootMeanSquared": ("среднеквадратичное значение плотности", "непрерывный, HU, $\\geq 0$"),
    "firstorder_Skewness": ("асимметрия распределения плотностей", "непрерывный"),
    "glcm_ClusterProminence": ("GLCM: выраженность кластеров уровней серого", "непрерывный, $\\geq 0$"),
    "glcm_ClusterShade": ("GLCM: асимметрия кластеров", "непрерывный"),
    "glcm_Correlation": ("GLCM: корреляция уровней соседних вокселей", "непрерывный, $[-1; 1]$"),
    "glcm_Idmn": ("GLCM: нормированный обратный момент разности (однородность)", "непрерывный, (0; 1]"),
    "glcm_Imc1": ("GLCM: информационная мера корреляции 1", "непрерывный, $[-1; 0]$"),
    "glcm_InverseVariance": ("GLCM: обратная дисперсия", "непрерывный, $\\geq 0$"),
    "glcm_MCC": ("GLCM: максимальный коэффициент корреляции", "непрерывный, [0; 1]"),
    "glcm_MaximumProbability": ("GLCM: частота наиболее частой пары уровней", "непрерывный, (0; 1]"),
    "glrlm_LongRunEmphasis": ("GLRLM: преобладание длинных серий", "непрерывный, $\\geq 1$"),
    "glrlm_LongRunHighGrayLevelEmphasis": ("GLRLM: длинные серии высоких уровней", "непрерывный, $>0$"),
    "glrlm_LongRunLowGrayLevelEmphasis": ("GLRLM: длинные серии низких уровней", "непрерывный, $>0$"),
    "glrlm_LowGrayLevelRunEmphasis": ("GLRLM: преобладание серий низких уровней", "непрерывный, (0; 1]"),
    "glrlm_RunEntropy": ("GLRLM: энтропия серий", "непрерывный, бит, $\\geq 0$"),
    "glszm_LargeAreaEmphasis": ("GLSZM: преобладание крупных зон", "непрерывный, $\\geq 1$"),
    "glszm_LargeAreaLowGrayLevelEmphasis": ("GLSZM: крупные зоны низких уровней", "непрерывный, $>0$"),
    "glszm_SizeZoneNonUniformity": ("GLSZM: неоднородность размеров зон", "непрерывный, $>0$"),
    "glszm_SizeZoneNonUniformityNormalized": ("GLSZM: нормированная неоднородность размеров зон",
                                              "непрерывный, (0; 1]"),
    "gldm_DependenceNonUniformityNormalized": ("GLDM: нормированная неоднородность зависимостей",
                                               "непрерывный, (0; 1]"),
    "gldm_SmallDependenceEmphasis": ("GLDM: преобладание малых зависимостей", "непрерывный, (0; 1]"),
    "gldm_SmallDependenceLowGrayLevelEmphasis": ("GLDM: малые зависимости низких уровней", "непрерывный, (0; 1]"),
    "ngtdm_Contrast": ("NGTDM: контраст соседних тонов", "непрерывный, $\\geq 0$"),
    "ngtdm_Strength": ("NGTDM: сила текстуры", "непрерывный, $\\geq 0$"),
}

rows = []
for name, meaning, typ, moment, decision in clinical:
    rows.append((tt(name), meaning, typ, moment, miss(name), decision))

rad_kept = [k for k in kept if k.startswith("GTVp_")]
assert set(radiomic_meaning) == {k.removeprefix("GTVp_") for k in rad_kept}
for k in rad_kept:
    meaning, typ = radiomic_meaning[k.removeprefix("GTVp_")]
    names = [f.removeprefix("GTVp_") for f in list(replaced_by) + list(duplicates) if root(f) == k]
    n = len(names)
    word = "исключённый признак" if n % 10 == 1 and n % 100 != 11 else "исключённых признака" if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else "исключённых признаков"
    dec = f"оставить; заменяет {n} {word}"
    if names:
        dec += ": " + ", ".join(re.sub(r"(?<=[a-z])(?=[A-Z])", r"\\allowbreak{}", n_.replace("_", "\\_\\allowbreak{}"))
                                for n_ in names)
    rows.append((tt(k), meaning + " (GTVp)", typ, CT, miss(k), dec))

with open("dictionary_rows.tex", "w") as f:
    for r in rows:
        f.write(" & ".join(r) + r" \\" + "\n")
print(f"строк словаря: {len(rows)} (клинических и служебных {len(clinical)}, радиомических {len(rad_kept)})")
