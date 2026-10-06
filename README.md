# Научная студия. Вычислительная онкология

Семестровая работа команды 04: прогнозирование локального рецидива рака ротоглотки после лучевой терапии
по КТ-радиомике и клиническим данным.

Набор данных: MICCAI 2016 / MD Anderson, задача локального рецидива
(Elhalawani et al., *Sci Data* 2017, doi:10.1038/sdata.2017.77). Снимки и исходные таблицы лежат вне репозитория:
`/Users/a1pha/oropharynx_cancer_data` (`Training/`, `Test/`, `Training.csv`, `Test.csv`).

## Структура

| Путь | Что это |
|---|---|
| `participants.txt` | ФИО участников команды (общий для всех недель) |
| `w3/` | Неделя 3 «Данные и радиомика» |
| `w3/practice.ipynb` | визуализация КТ и масок, извлечение признаков PyRadiomics, сборка таблицы |
| `w3/dataset.csv` | 298 пациентов × 235 столбцов: `Patient_ID`, `Fold`, 18 клинических, 107 `GTVp_*`, 107 `GTVn_*`, `GTVn_n_nodes` |
| `w3/text/` | LaTeX-отчёт: `main.tex`, `source.bib`, `fig/`, собранный `main.pdf` |
| `w4/` | Неделя 4 «Общий анализ данных» |
| `w4/practice.ipynb` | проверка значений, целевая переменная, отбор признаков, аналитическая таблица; читает `w3/dataset.csv` |
| `w4/analytic_table.csv` | 140 пациентов: `Patient_ID`, `Target_local_recurrence`, 102 признака |
| `w4/text/` | LaTeX-отчёт: `text.tex`, `references.bib`, словарь переменных `dictionary_rows.tex`, `logo.png`, собранный `text.pdf` |
| `make_submission.sh` | сборка архива для сдачи |

## Окружение

```bash
python3.14 -m venv .venv
.venv/bin/pip install numpy setuptools wheel
.venv/bin/pip install -r requirements.txt
```

pyradiomics 3.1.0 с PyPI не собирается под Python 3.14, поэтому ставится из GitHub (закреплённый коммит).
Неделе 4 нужны только numpy, pandas и matplotlib.

## Запуск

Ноутбуки читают и пишут файлы относительно своей папки, поэтому запускаются из неё:

```bash
cd w3 && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 practice.ipynb
cd w4 && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace practice.ipynb
```

Извлечение признаков недели 3 занимает около 20 минут на 315 пациентов; неделя 4 считается за секунды.

Отчёты собираются LaTeX (pdfLaTeX + biber):

```bash
cd w3/text && latexmk -pdf main.tex
cd w4/text && latexmk -pdf text.tex
```

## Сдача

```bash
./make_submission.sh 3 04   # w3_team04.zip: participants.txt, practice.ipynb, text.pdf, dataset.csv
./make_submission.sh 4 04   # w4_team04.zip: participants.txt, practice.ipynb, text.pdf, analytic_table.csv
```
