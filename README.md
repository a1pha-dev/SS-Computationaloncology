# Вычислительная онкология — неделя 3: данные и радиомика

Набор данных: MICCAI 2016 / MD Anderson, рак ротоглотки, задача локального рецидива
(Elhalawani et al., *Sci Data* 2017, doi:10.1038/sdata.2017.77). Данные лежат вне репозитория:
`/Users/a1pha/oropharynx_cancer_data` (`Training/`, `Test/`, `Training.csv`, `Test.csv`).

| Файл | Что это |
|---|---|
| `practice.ipynb` | визуализация КТ + масок, извлечение признаков PyRadiomics для всех пациентов, сборка таблицы (выполнен, с выводом) |
| `dataset.csv` | 298 пациентов × 127 столбцов: `Patient_ID`, `Fold`, 18 клинических, 107 радиомических признаков `GTVp_*` |
| `text/text.tex`, `text/text.pdf` | «Материалы и методы»: описание набора и протокол извлечения |
| `participants.txt` | ФИО участников (заполнить) |
| `make_submission.sh` | собирает `w3_teamNN.zip` |

## Окружение

```bash
python3.14 -m venv .venv
.venv/bin/pip install numpy setuptools wheel
.venv/bin/pip install -r requirements.txt
.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 practice.ipynb
```

pyradiomics 3.1.0 с PyPI не собирается под Python 3.14, поэтому ставится из GitHub (закреплённый коммит).
Полный прогон извлечения — около 20 минут на 315 пациентов.

## Сдача

```bash
./make_submission.sh 07
```
