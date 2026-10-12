# Эмулятор UNIX-подобной оболочки — вариант №19

Практическая работа выполнена по требованиям варианта №19.

## Что реализовано

### Этап 1 — REPL
- CLI-интерфейс.
- Приглашение формируется из реальных `username` и `hostname`.
- Формат приглашения: `username@hostname:/path$`.
- Простой парсер: команда и аргументы разделяются пробелами.
- Ошибки неизвестных команд и неверных аргументов.
- Команды-заглушки/команды оболочки: `ls`, `cd`.
- `exit`.

### Этап 2 — конфигурация
Параметры командной строки:
- `--vfs PATH`
- `--script PATH`

Стартовый скрипт выполняется последовательно и останавливается при первой ошибке. На экран выводятся ввод и вывод.

### Этап 3 — VFS
- Источник VFS — обычная директория на диске.
- При запуске содержимое загружается в память.
- Команды работают только с in-memory представлением.
- Изменения `touch` и `rmdir` не изменяют исходную директорию.

### Этап 4 — основные команды
- `ls [path]`
- `cd <path>`
- `head [-n N] <file>`
- `cal [month year]`

### Этап 5 — дополнительные команды
- `touch <file>`
- `rmdir <directory>`

## Структура

```text
variant19_shell_emulator/
├── src/
│   ├── __init__.py
│   ├── commands.py
│   ├── main.py
│   └── vfs.py
├── tests/
│   ├── conftest.py
│   ├── test_commands.py
│   └── test_vfs.py
├── vfs/
│   ├── minimal/
│   └── sample/
├── examples/
│   ├── startup_ok.txt
│   └── startup_error.txt
├── scripts/
│   ├── run_minimal.sh
│   ├── run_sample.sh
│   └── run_error.sh
├── .gitignore
├── requirements.txt
├── run.sh
└── README.md
```

## Требования

Python 3.10+.

Установка зависимостей:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск REPL

```bash
python -m src.main --vfs ./vfs/sample
```

После запуска:

```text
username@hostname:/$ ls
```

## Запуск стартового скрипта

```bash
./run.sh --vfs ./vfs/sample --script ./examples/startup_ok.txt
```

Скрипт с ошибкой:

```bash
./run.sh --vfs ./vfs/sample --script ./examples/startup_error.txt
```

Он должен завершиться с ненулевым кодом после `unknown_command`.

## Команды

### ls

```text
ls
ls docs
```

Показывает содержимое каталога.

### cd

```text
cd docs
cd ..
cd /
```

Меняет текущий каталог VFS.

### head

```text
head file.txt
head -n 3 file.txt
```

Выводит первые 10 строк либо заданное количество строк.

### cal

```text
cal
cal 1 2025
```

Показывает календарь текущего месяца либо указанного месяца.

### touch

```text
touch new.txt
```

Создаёт файл только в памяти VFS.

### rmdir

```text
rmdir empty
```

Удаляет пустой каталог только из памяти VFS.

### exit

Завершает эмулятор.

## Тестирование

```bash
pytest -q
```

Тесты проверяют:
- загрузку VFS;
- `ls` и `cd`;
- `head`;
- `cal`;
- `touch`;
- `rmdir`;
- обработку неизвестной команды;
- обработку неверных аргументов;
- отсутствие записи `touch` на физический диск.

## Примеры скриптов реальной ОС

```bash
./scripts/run_minimal.sh
./scripts/run_sample.sh
./scripts/run_error.sh
```

## Ограничение VFS

Физическая директория используется только как источник данных при запуске. Все изменения, выполняемые командами оболочки, производятся в памяти и не записываются обратно на диск.

## Демонстрационный каталог empty

Каталог `vfs/sample/empty/` намеренно оставлен полностью пустым, чтобы команда `rmdir empty` могла успешно продемонстрировать удаление пустого каталога из VFS в памяти.
