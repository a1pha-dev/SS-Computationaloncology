# Научная студия. Вычислительная онкология

Семестровая работа команды 04: прогнозирование локального рецидива рака ротоглотки после лучевой терапии
по КТ-радиомике и клиническим данным.

Набор данных: MICCAI 2016 / MD Anderson, задача локального рецидива
(Elhalawani et al., *Sci Data* 2017, doi:10.1038/sdata.2017.77). Снимки и исходные таблицы лежат вне репозитория:
`/Users/a1pha/oropharynx_cancer_data` (`Training/`, `Test/`, `Training.csv`, `Test.csv`).

## Структура

Каждая неделя лежит в своей папке `w<i>/` с одинаковой раскладкой:

```
w<i>/
  practice.ipynb      ноутбук с сохранённым выводом
  <таблица>.csv       сдаваемая таблица недели (ровно одна)
  text/
    main.tex          отчёт (LaTeX)
    source.bib        литература
    fig/              рисунки и логотип
    main.pdf          собранный отчёт
```

| Неделя | Тема | Таблица |
|---|---|---|
| `w3/` | Данные и радиомика | `dataset.csv` — 298 пациентов × 235 столбцов: `Patient_ID`, `Fold`, 18 клинических, 107 `GTVp_*`, 107 `GTVn_*`, `GTVn_n_nodes` |
| `w4/` | Общий анализ данных | `analytic_table.csv` — 140 пациентов: `Patient_ID`, `Target_local_recurrence`, 52 признака; ноутбук читает `../w3/dataset.csv`, словарь переменных — `text/dictionary_rows.tex` |

В корне: `participants.txt` (участники команды, общий для всех недель), `make_submission.sh`, `requirements.txt`.

## Окружение

```bash
python3.14 -m venv .venv
.venv/bin/pip install numpy setuptools wheel
.venv/bin/pip install -r requirements.txt
```

pyradiomics 3.1.0 с PyPI не собирается под Python 3.14, поэтому ставится из GitHub (закреплённый коммит).
Неделе 4 нужны только numpy, pandas, matplotlib и seaborn.

## Сборка недели `w<i>`

Ноутбук читает и пишет файлы относительно своей папки, поэтому запускается из неё; отчёт собирается pdfLaTeX + biber:

```bash
cd w<i> && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 practice.ipynb
cd w<i>/text && latexmk -pdf main.tex && latexmk -c
```

Извлечение признаков недели 3 занимает около 20 минут на 315 пациентов, остальные ноутбуки считаются за секунды.

## Сдача недели `w<i>`

```bash
./make_submission.sh <i> 04
```

Скрипт собирает `w<i>_team04.zip` без вложенных папок: `participants.txt`, `practice.ipynb`, `text.pdf` (из `w<i>/text/main.pdf`) и таблицу `w<i>/*.csv`.
