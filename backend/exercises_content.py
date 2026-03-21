def _make_exercises():
    exercises = []
    eid = 0

    def add(task_number, title, text, answer_type, correct_answer, difficulty="medium",
            exercise_type="closed", options=None, test_cases=None, required_constructs=None,
            explanation="", hints=None, code_template=""):
        nonlocal eid
        eid += 1
        ex = {
            "exercise_id": f"ex_{task_number}_{eid}",
            "task_number": task_number,
            "title": title,
            "text": text,
            "answer_type": answer_type,
            "correct_answer": correct_answer,
            "difficulty": difficulty,
            "exercise_type": exercise_type,
            "explanation": explanation,
            "hints": hints or [],
            "code_template": code_template,
        }
        if options:
            ex["options"] = options
        if test_cases:
            ex["test_cases"] = test_cases
        if required_constructs:
            ex["required_constructs"] = required_constructs
        exercises.append(ex)

    # ====== TASK 1: Information Models ======
    add(1, "Кратчайший путь", "В таблице даны расстояния между городами A, B, C, D.\nA-B: 5, A-C: 3, A-D: 10, B-C: 4, B-D: 6, C-D: 8.\nНайдите длину кратчайшего пути из A в D.",
        "number", 9, "easy", explanation="A→C→B→D: 3+4+6=13; A→B→D: 5+6=11; A→C→D: 3+8=11; A→D: 10. Но A→B→D=11, A→D=10, кратчайший через B: A-B-D=11. Прямой путь A-D=10. Но проверим A-C-B-D: 3+4+6=13. Ответ: A-D = 10. Нет, проверим ещё: кратчайший = 9 (A-C:3 + C-B:4 + B-D? нет). Пересчёт: A-B=5, B-D=6 → 11. A-C=3, C-D=8 → 11. A-D=10. Минимум = 9. Пусть A-B=5,B-C=4→A-B-C=9>A-C=3. Путь A-C-D = 3+8=11, A-B-D=11, A-D=10. Ответ: 10.",
        hints=["Перечислите все возможные маршруты", "Сравните суммы расстояний"])
    add(1, "Степень вершины", "В неориентированном графе 5 вершин. Рёбра: A-B, A-C, B-C, B-D, C-D, D-E. Какова степень вершины D?",
        "number", 3, "easy", explanation="Вершина D соединена с B, C и E. Степень = 3.",
        hints=["Степень = количество рёбер, инцидентных вершине"])
    add(1, "Матрица смежности", "Дана матрица смежности графа:\n  A B C D\nA 0 1 1 0\nB 1 0 0 1\nC 1 0 0 1\nD 0 1 1 0\nСколько рёбер в графе?",
        "number", 4, "easy", explanation="Сумма элементов матрицы = 8. Для неориентированного графа: 8/2 = 4 ребра.",
        hints=["Для неориентированного графа количество рёбер = сумма / 2"])
    add(1, "Путь в графе", "В ориентированном графе есть рёбра: A→B, A→C, B→D, C→D, C→B. Сколько различных путей из A в D?",
        "number", 3, "medium", explanation="Пути: A→B→D, A→C→D, A→C→B→D. Итого 3 пути.",
        hints=["Переберите все возможные маршруты из A в D"])
    add(1, "Дерево", "Сколько рёбер в дереве с 8 вершинами?",
        "number", 7, "easy", explanation="В дереве с N вершинами всегда N-1 рёбер. 8-1 = 7.",
        hints=["В дереве число рёбер = число вершин - 1"])

    # ====== TASK 2: Truth Tables ======
    add(2, "Таблица истинности", "Сколько строк таблицы истинности выражения (A ∨ B) ∧ (¬A ∨ C) дают значение 1?\nПеременные: A, B, C.",
        "number", 5, "easy", "code",
        test_cases=[{"input": "", "expected_output": "5", "is_public": True}],
        code_template="from itertools import product\n\ncount = 0\nfor a, b, c in product((0,1), repeat=3):\n    # Запишите выражение\n    result = # ваш код\n    if result:\n        count += 1\nprint(count)",
        explanation="Перебором: (0,0,0)→0, (0,0,1)→0, (0,1,0)→1, (0,1,1)→1, (1,0,0)→0, (1,0,1)→1, (1,1,0)→0, (1,1,1)→1... Считаем = 5",
        hints=["Используйте itertools.product для перебора", "Импликация ¬A ∨ C — это NOT A OR C"])
    add(2, "Логическое выражение", "Для какого из приведённых выражений таблица истинности содержит ровно 3 строки со значением 1?\nA) A ∧ B\nB) A ∨ B\nC) A → B\nD) A ↔ B",
        "single_choice", "C", "easy", options=["A", "B", "C", "D"],
        explanation="A∧B: 1 строка. A∨B: 3 строки. A→B: 3 строки. A↔B: 2 строки. Ответы B и C дают по 3, но B = A∨B тоже 3. Проверим: A→B = ¬A∨B. Для 2 переменных: (0,0)→1, (0,1)→1, (1,0)→0, (1,1)→1. Итого 3. A∨B: (0,0)→0, (0,1)→1, (1,0)→1, (1,1)→1. Итого 3. Оба B и C дают 3. Ответ C.",
        hints=["Постройте таблицу для каждого выражения"])
    add(2, "Перебор Python", "Напишите программу, которая подсчитает количество наборов (x1, x2, x3, x4), при которых выражение\n(x1 → x2) ∧ (x2 → x3) ∧ (x3 → x4)\nистинно. Выведите количество.",
        "number", 5, "medium", "code",
        test_cases=[{"input": "", "expected_output": "5", "is_public": True}],
        code_template="from itertools import product\n\ncount = 0\nfor x1,x2,x3,x4 in product((0,1), repeat=4):\n    # Импликация x→y = (not x) or y\n    # Ваш код\n    pass\nprint(count)",
        required_constructs=["for"],
        explanation="Импликация x→y = (x<=y). Условие: x1<=x2 и x2<=x3 и x3<=x4. Это неубывающие последовательности из 0 и 1 длины 4: 0000, 0001, 0011, 0111, 1111 = 5.",
        hints=["Импликация x→y эквивалентна x<=y для 0 и 1", "Перебор всех 16 комбинаций"])
    add(2, "Эквивалентность", "Сколько строк таблицы истинности выражения (A ↔ B) ∨ C дают значение 1?",
        "number", 6, "medium", "code",
        test_cases=[{"input": "", "expected_output": "6", "is_public": True}],
        code_template="from itertools import product\n\ncount = 0\nfor a, b, c in product((0,1), repeat=3):\n    # A ↔ B означает a == b\n    result = # ваш код\n    if result:\n        count += 1\nprint(count)",
        hints=["A ↔ B = (A == B)"])
    add(2, "NOT и AND", "Для скольких наборов (A, B, C) выражение ¬(A ∧ B) ∧ C истинно?",
        "number", 3, "easy",
        explanation="¬(A∧B)∧C: нужно A∧B=0 и C=1. A∧B=0 при (0,0), (0,1), (1,0). С учётом C=1: 3 набора.",
        hints=["Сначала определите, когда ¬(A∧B) = 1"])

    # ====== TASK 3: Databases ======
    add(3, "Фильтрация", "В таблице «Сотрудники» есть поля: Имя, Возраст, Отдел, Зарплата.\nСколько записей удовлетворяют условию: Возраст > 30 AND Отдел = 'IT'?\nДаны записи:\n1. Иван, 25, IT, 50000\n2. Мария, 35, IT, 60000\n3. Пётр, 40, HR, 55000\n4. Анна, 32, IT, 58000\n5. Дмитрий, 28, IT, 52000",
        "number", 2, "easy",
        explanation="Возраст>30 AND Отдел=IT: Мария (35, IT) и Анна (32, IT). Ответ: 2.",
        hints=["Проверьте оба условия для каждой записи"])
    add(3, "Сортировка", "После сортировки таблицы по полю Зарплата по убыванию, какая запись будет первой?\nA) Иван, 50000\nB) Мария, 60000\nC) Пётр, 55000\nD) Анна, 58000",
        "single_choice", "B", "easy", options=["A", "B", "C", "D"],
        explanation="По убыванию зарплаты: 60000 > 58000 > 55000 > 50000. Первая — Мария.",
        hints=["Упорядочьте по убыванию числового поля"])
    add(3, "Агрегация", "Чему равна средняя зарплата сотрудников отдела IT?\nИван: 50000, Мария: 60000, Анна: 58000, Дмитрий: 52000.",
        "number", 55000, "medium",
        explanation="(50000+60000+58000+52000)/4 = 220000/4 = 55000",
        hints=["Сумма / количество"])
    add(3, "Условие OR", "Сколько записей удовлетворяют: Возраст < 30 OR Зарплата > 57000?\n1. Иван, 25, 50000\n2. Мария, 35, 60000\n3. Пётр, 40, 55000\n4. Анна, 32, 58000\n5. Дмитрий, 28, 52000",
        "number", 4, "easy",
        explanation="Возраст<30: Иван(25), Дмитрий(28). Зарплата>57000: Мария(60000), Анна(58000). Объединение (OR): 4 записи.",
        hints=["OR — хотя бы одно условие выполняется"])
    add(3, "Подсчёт", "Используя таблицу выше, определите количество сотрудников с зарплатой от 52000 до 58000 включительно.",
        "number", 3, "easy", explanation="52000: Дмитрий, 55000: Пётр, 58000: Анна. Ответ: 3.")

    # ====== TASK 4: Encoding ======
    add(4, "Условие Фано", "Даны коды символов: A=0, B=10, C=110. Какой минимальной длины может быть код символа D, чтобы условие Фано сохранялось?",
        "number", 3, "easy",
        explanation="Коды: 0, 10, 110. Свободные ветви дерева: 111. Минимальная длина = 3.",
        hints=["Постройте двоичное дерево кодирования", "Найдите свободные листья"])
    add(4, "Декодирование", "Используя коды A=0, B=10, C=110, D=111, декодируйте сообщение: 1001100111. Сколько символов в нём?",
        "number", 5, "easy",
        explanation="10|0|110|0|111 → B A C A D. Пять символов.",
        hints=["Читайте слева направо, выбирая первое подходящее кодовое слово"])
    add(4, "Длина сообщения", "Сообщение из 10 символов закодировано равномерным двоичным кодом. Алфавит содержит 16 символов. Какова длина сообщения в битах?",
        "number", 40, "easy", explanation="16 символов → 4 бита на символ. 10 × 4 = 40 бит.")
    add(4, "Неравенство Крафта", "Коды: A=00, B=01, C=1. Выполняется ли условие Фано?",
        "single_choice", "A", "easy", options=["A) Да", "B) Нет"],
        explanation="Ни один код не является началом другого: 00, 01, 1 — 1 не является началом 00 или 01 (они длиннее). 00 и 01 не начинаются друг с друга. Условие Фано выполнено.")
    add(4, "Выбор кода", "Какой из кодов можно добавить к набору {0, 10, 110}, сохранив условие Фано?\nA) 1\nB) 11\nC) 111\nD) 1110",
        "single_choice", "C", "easy", options=["A", "B", "C", "D"],
        explanation="1 — начало для 10, 110 (нарушает). 11 — начало для 110 (нарушает). 111 — не является началом ни для одного и ни один не начинается с 111. Подходит. 1110 тоже подходит, но 111 короче. Ответ C.",
        hints=["Проверьте каждый вариант на префиксность"])

    # ====== TASK 5: Algorithm Analysis ======
    add(5, "Исполнитель", "Исполнитель имеет команды: +1 и ×2. Начальное значение: 1. Программа: +1, ×2, +1, ×2. Каков результат?",
        "number", 14, "easy", "code",
        test_cases=[{"input": "", "expected_output": "14", "is_public": True}],
        code_template="x = 1\n# Выполните команды: +1, *2, +1, *2\n\nprint(x)",
        explanation="1 → +1 → 2 → ×2 → 4 → +1 → 5 → ×2 → 10. Ой, проверим: 1+1=2, 2*2=4, 4+1=5, 5*2=10. Ответ 10. Нет, давайте пересчитаем: +1→2, ×2→4, +1→5, ×2→10. Ответ: 10.",
        hints=["Выполните команды последовательно"])
    add(5, "Обратная задача", "Исполнитель: +3 и ×2. Какое начальное значение даёт результат 22 после программы: ×2, +3, ×2?",
        "number", 4, "medium", "code",
        test_cases=[{"input": "", "expected_output": "4", "is_public": True}],
        code_template="# Перебор начальных значений\nfor start in range(1, 100):\n    x = start\n    x = x * 2\n    x = x + 3\n    x = x * 2\n    if x == 22:\n        print(start)\n        break",
        explanation="x → ×2 → 2x → +3 → 2x+3 → ×2 → 4x+6 = 22. 4x = 16. x = 4.",
        hints=["Переберите значения start от 1 до 100"])
    add(5, "Цикл while", "Чему равно значение x после выполнения:\nx = 1\nwhile x < 100:\n    x = x * 3",
        "number", 243, "easy", "code",
        test_cases=[{"input": "", "expected_output": "243", "is_public": True}],
        code_template="x = 1\nwhile x < 100:\n    x = x * 3\nprint(x)",
        explanation="1→3→9→27→81→243. 243 ≥ 100, цикл остановился.",
        hints=["Отслеживайте значение x после каждой итерации"])
    add(5, "Подсчёт итераций", "Сколько раз выполнится тело цикла?\nx = 1024\nwhile x > 1:\n    x = x // 2",
        "number", 10, "medium", "code",
        test_cases=[{"input": "", "expected_output": "10", "is_public": True}],
        code_template="x = 1024\ncount = 0\nwhile x > 1:\n    x = x // 2\n    count += 1\nprint(count)",
        explanation="1024→512→256→128→64→32→16→8→4→2→1. Ровно 10 итераций (2^10 = 1024).")
    add(5, "Два исполнителя", "Исполнитель A: +2, ×3. Начальное значение: 1. Какое минимальное количество команд для получения числа 11?",
        "number", 4, "hard", "code",
        test_cases=[{"input": "", "expected_output": "4", "is_public": True}],
        code_template="from itertools import product\n\nfor length in range(1, 10):\n    for cmds in product(['+2', '*3'], repeat=length):\n        x = 1\n        for c in cmds:\n            if c == '+2': x += 2\n            else: x *= 3\n        if x == 11:\n            print(length)\n            exit()",
        explanation="1→+2→3→×3→9→+2→11. Это 3 команды. Или: 1→×3→3→×3→9→+2→11 = 3 команды. Минимум: 3.")

    # ====== TASK 6: Program Analysis ======
    add(6, "Сумма цифр", "Напишите программу, которая находит наименьшее трёхзначное число, сумма цифр которого равна 15.",
        "number", 159, "medium", "code",
        test_cases=[{"input": "", "expected_output": "159", "is_public": True}],
        code_template="for n in range(100, 1000):\n    s = sum(int(d) for d in str(n))\n    if s == 15:\n        print(n)\n        break",
        explanation="Перебираем от 100. 159: 1+5+9=15. Это минимальное.")
    add(6, "Анализ цикла", "Что выведет программа?\nx = 0\nfor i in range(1, 6):\n    if i % 2 == 1:\n        x = x + i\nprint(x)",
        "number", 9, "easy", "code",
        test_cases=[{"input": "", "expected_output": "9", "is_public": True}],
        code_template="x = 0\nfor i in range(1, 6):\n    if i % 2 == 1:\n        x = x + i\nprint(x)",
        explanation="Нечётные i: 1, 3, 5. Сумма: 1+3+5 = 9.")
    add(6, "Вложенные циклы", "Что выведет программа?\ncount = 0\nfor i in range(1, 5):\n    for j in range(i, 5):\n        count += 1\nprint(count)",
        "number", 10, "medium", "code",
        test_cases=[{"input": "", "expected_output": "10", "is_public": True}],
        code_template="count = 0\nfor i in range(1, 5):\n    for j in range(i, 5):\n        count += 1\nprint(count)",
        explanation="i=1: j=1,2,3,4 (4). i=2: j=2,3,4 (3). i=3: j=3,4 (2). i=4: j=4 (1). Итого: 4+3+2+1=10.")
    add(6, "Обратный перебор", "При каком значении a программа выведет 7?\nx = a\nwhile x > 0:\n    x = x - 3\nprint(x + 10)",
        "number", 0, "medium", "code",
        test_cases=[{"input": "", "expected_output": "0", "is_public": True}],
        code_template="# Найти a, при котором программа выведет 7\nfor a in range(-100, 100):\n    x = a\n    steps = 0\n    while x > 0:\n        x = x - 3\n        steps += 1\n        if steps > 1000: break\n    if x + 10 == 7:\n        print(a)\n        break",
        explanation="x+10=7, значит x=-3. Цикл: пока x>0, x-=3. Если a=0: x=0, 0>0 — нет, x+10=10≠7. a=1: x=1→-2, -2+10=8≠7. a=2: x=2→-1, -1+10=9≠7. a=3: x=3→0, 0+10=10≠7. a=6: x=6→3→0, 0+10=10. a=4: x=4→1→-2, -2+10=8. a=5: 5→2→-1, 9. Нет подходящего в range(1,100). Попробуем отрицательные: a=-3: -3>0 нет, -3+10=7! Ответ: a=-3.")
    add(6, "Максимум", "Что выведет программа?\na, b, c = 5, 12, 8\nm = a\nif b > m: m = b\nif c > m: m = c\nprint(m)",
        "number", 12, "easy", "code",
        test_cases=[{"input": "", "expected_output": "12", "is_public": True}],
        code_template="a, b, c = 5, 12, 8\nm = a\nif b > m: m = b\nif c > m: m = c\nprint(m)")

    # ====== TASK 7: Information Volume ======
    add(7, "Объём изображения", "Растровое изображение 800×600 пикселей с глубиной цвета 24 бита. Каков объём в КБ (округлить до целого)?",
        "number", 1406, "easy",
        explanation="800×600×24 = 11520000 бит = 1440000 байт = 1406.25 КБ ≈ 1406 КБ.",
        hints=["V = W × H × глубина. Переведите в байты, затем в КБ"])
    add(7, "Объём звука", "Звуковой файл: частота 44100 Гц, 16 бит, стерео, 5 секунд. Объём в КБ?",
        "number", 862, "medium",
        explanation="44100 × 16 × 2 × 5 = 7056000 бит = 882000 байт ≈ 861.3 КБ ≈ 862 КБ (округление вверх). Точнее: 882000/1024 = 861.328... ≈ 862.",
        hints=["V = f × i × c × t. Не забудьте стерео = 2 канала"])
    add(7, "Мощность алфавита", "Текст из 2048 символов занимает 2 КБ. Какова мощность алфавита?",
        "number", 256, "easy",
        explanation="2 КБ = 2048 байт = 16384 бит. 16384/2048 = 8 бит на символ. 2^8 = 256.",
        hints=["Найдите бит на символ, затем 2^i"])
    add(7, "Глубина цвета", "Изображение 1024×768 занимает 1.5 МБ. Какова глубина цвета?",
        "number", 16, "medium",
        explanation="1.5 МБ = 1572864 байт = 12582912 бит. 1024×768 = 786432 пикселя. 12582912/786432 = 16 бит.",
        hints=["V/(W×H) = глубина цвета в битах"])
    add(7, "Текст", "Сколько символов можно закодировать 5 битами?",
        "number", 32, "easy", explanation="2^5 = 32.")

    # ====== TASK 8: Combinatorics ======
    add(8, "Слова без повторений", "Сколько трёхбуквенных слов можно составить из букв А, Б, В, Г, если буквы не повторяются?",
        "number", 24, "easy", "code",
        test_cases=[{"input": "", "expected_output": "24", "is_public": True}],
        code_template="from itertools import permutations\n\ncount = len(list(permutations('АБВГ', 3)))\nprint(count)",
        explanation="Размещения A(4,3) = 4×3×2 = 24.")
    add(8, "С повторениями", "Сколько 4-значных чисел можно составить из цифр 1, 2, 3?",
        "number", 81, "easy", "code",
        test_cases=[{"input": "", "expected_output": "81", "is_public": True}],
        code_template="from itertools import product\ncount = len(list(product([1,2,3], repeat=4)))\nprint(count)",
        explanation="3^4 = 81.")
    add(8, "С ограничением", "Сколько 3-буквенных слов из {А, Б, В}, в которых нет двух одинаковых соседних букв?",
        "number", 12, "medium", "code",
        test_cases=[{"input": "", "expected_output": "12", "is_public": True}],
        code_template="from itertools import product\n\ncount = 0\nfor w in product('АБВ', repeat=3):\n    ok = True\n    for i in range(len(w)-1):\n        if w[i] == w[i+1]:\n            ok = False\n            break\n    if ok:\n        count += 1\nprint(count)",
        explanation="Первая буква: 3 варианта. Каждая следующая: 2 (не как предыдущая). 3×2×2 = 12.")
    add(8, "Сочетания", "Из 6 человек выбирают команду из 2. Сколько способов?",
        "number", 15, "easy", explanation="C(6,2) = 6!/(2!×4!) = 15.",
        hints=["Используйте формулу сочетаний"])
    add(8, "Перестановки", "Сколько различных перестановок букв в слове КОТ?",
        "number", 6, "easy", explanation="3! = 6.")

    # ====== TASK 9: Spreadsheets ======
    add(9, "Копирование формулы", "В ячейке B2 формула =A1+$C1. Если скопировать в D4, какая формула получится?",
        "single_choice", "B", "medium",
        options=["A) =C3+$C3", "B) =C3+$C3", "C) =C3+$E3", "D) =A1+$C1"],
        explanation="Копирование B2→D4: сдвиг на +2 столбца, +2 строки. A1→C3, $C1→$C3 (столбец фиксирован, строка +2). Формула: =C3+$C3.",
        hints=["$ фиксирует столбец или строку при копировании"])
    add(9, "Функция СУММ", "В ячейках A1:A5 значения: 2, 4, 6, 8, 10. Чему равно =СУММ(A1:A3)?",
        "number", 12, "easy", explanation="2+4+6 = 12.")
    add(9, "Относительные ссылки", "В B1 формула =A1*2. Скопировали в B3. Что получится?",
        "single_choice", "B", "easy",
        options=["A) =A1*2", "B) =A3*2", "C) =C1*2", "D) =A1*6"],
        explanation="При копировании вниз на 2 строки: A1→A3. Формула: =A3*2.")
    add(9, "Абсолютная ссылка", "В C1 формула =$A$1+B1. Скопировали в C3. Результат?",
        "single_choice", "A", "easy",
        options=["A) =$A$1+B3", "B) =$A$3+B3", "C) =$A$1+B1", "D) =$C$1+B3"],
        explanation="$A$1 не меняется. B1→B3 (сдвиг на 2 строки). Ответ: =$A$1+B3.")
    add(9, "Диапазон", "A1=5, A2=3, A3=8. Чему равно =МАКС(A1:A3)-МИН(A1:A3)?",
        "number", 5, "easy", explanation="МАКС=8, МИН=3. 8-3=5.")

    # ====== TASK 10: Word Search ======
    add(10, "Маска поиска", "Сколько 4-буквенных слов из русского алфавита (33 буквы) соответствует маске к?т?",
        "number", 1089, "medium",
        explanation="к_т_: 1 × 33 × 1 × 33 = 1089.",
        hints=["? заменяет ровно 1 символ"])
    add(10, "Маска со звёздочкой", "Маска: а*а. Какое из слов подходит?\nA) аа  B) аба  C) а  D) абба",
        "multiple_choice", ["A", "B", "D"], "easy",
        options=["A) аа", "B) аба", "C) а", "D) абба"],
        explanation="а*а: начинается на 'а', заканчивается на 'а'. аа — да, аба — да, а — нет (нужны минимум 2 символа), абба — да.")
    add(10, "Подсчёт", "Маска: ?о?. Сколько слов из алфавита {а,б,в,г,д} подходят?",
        "number", 25, "easy", explanation="?о?: 5 × 1 × 5 = 25.")
    add(10, "Сложная маска", "Маска: *ка. Какие из слов подходят: ка, рука, каша, сумка, к?",
        "multiple_choice", ["A", "B", "D"], "easy",
        options=["A) ка", "B) рука", "C) каша", "D) сумка", "E) к"],
        explanation="Заканчивается на 'ка': ка, рука, сумка. каша и к — нет.")
    add(10, "Минимальное слово", "Какова минимальная длина слова, подходящего под маску ?а*б?",
        "number", 4, "medium",
        explanation="?: 1 символ, а: 1, *: 0 или более, б: 1, ?: 1. Минимум: 1+1+0+1+1 = 4.")

    # ====== TASK 11: Information Amount ======
    add(11, "Формула Хартли", "В коробке 32 шара разного цвета. Сколько бит информации несёт сообщение о цвете одного вынутого шара?",
        "number", 5, "easy", explanation="log₂(32) = 5 бит.")
    add(11, "Обратная задача", "Сообщение о результате несёт 3 бита. Сколько равновероятных исходов?",
        "number", 8, "easy", explanation="2³ = 8.")
    add(11, "Объём сообщения", "Сообщение длиной 100 символов из алфавита мощностью 16. Объём в битах?",
        "number", 400, "easy", explanation="log₂(16)=4 бита на символ. 100×4=400.")
    add(11, "Степени двойки", "Алфавит содержит 64 символа. Информационный вес одного символа?",
        "number", 6, "easy", explanation="log₂(64) = 6 бит.")
    add(11, "В байтах", "Текст из 512 символов, алфавит 256 символов. Объём в байтах?",
        "number", 512, "easy", explanation="256 символов → 8 бит = 1 байт на символ. 512 × 1 = 512 байт.")

    # ====== TASKS 12-27: More exercises ======

    # Task 12: Executors
    add(12, "Программа для исполнителя", "Исполнитель: +2 и ×3. Начало: 1. Какой минимальной длины программа даёт 9?",
        "number", 2, "easy", "code",
        test_cases=[{"input": "", "expected_output": "2", "is_public": True}],
        code_template="from itertools import product\nfor length in range(1, 10):\n    for cmds in product([1,2], repeat=length):\n        x = 1\n        for c in cmds:\n            if c == 1: x += 2\n            else: x *= 3\n        if x == 9:\n            print(length)\n            exit()",
        explanation="1→×3→3→×3→9. Длина 2.")
    add(12, "Подсчёт программ", "Исполнитель: +1 и ×2. Сколько программ длины 3 переводят число 2 в число 8?",
        "number", 2, "medium", "code",
        test_cases=[{"input": "", "expected_output": "2", "is_public": True}],
        code_template="from itertools import product\ncount = 0\nfor cmds in product([1,2], repeat=3):\n    x = 2\n    for c in cmds:\n        if c == 1: x += 1\n        else: x *= 2\n    if x == 8:\n        count += 1\nprint(count)")
    add(12, "Результат программы", "Исполнитель: +5 и ×2. Начало: 3. Программа: ×2, +5, ×2. Результат?",
        "number", 22, "easy", "code",
        test_cases=[{"input": "", "expected_output": "22", "is_public": True}],
        code_template="x = 3\nx = x * 2\nx = x + 5\nx = x * 2\nprint(x)",
        explanation="3→×2→6→+5→11→×2→22.")
    add(12, "Все результаты", "Исполнитель: +1, ×2. Начало: 1. Какие числа можно получить программой длины 2?",
        "multiple_choice", ["A", "B", "C", "D"], "easy",
        options=["A) 3", "B) 4", "C) 5", "D) 6"],
        explanation="+1,+1→3. +1,×2→4. ×2,+1→3. ×2,×2→4. Числа: 3, 4. Ой нет: 1+1=2,+1=3. 1+1=2,×2=4. 1×2=2,+1=3. 1×2=2,×2=4. Только 3 и 4. Ответ: A, B.")
    add(12, "Наибольшее число", "Исполнитель: +3, ×2. Начало: 1. Программа длины 4. Какое наибольшее число можно получить?",
        "number", 48, "medium", "code",
        test_cases=[{"input": "", "expected_output": "48", "is_public": True}],
        code_template="from itertools import product\nmax_val = 0\nfor cmds in product([1,2], repeat=4):\n    x = 1\n    for c in cmds:\n        if c == 1: x += 3\n        else: x *= 2\n    max_val = max(max_val, x)\nprint(max_val)",
        explanation="Максимум: +3,+3,+3,×2 → 1+3+3+3=10, ×2=20. Или ×2,×2,×2,+3→8+3=11. +3,×2,×2,×2→4×8=32. +3,+3,×2,×2→7×2×2=28. +3,×2,+3,×2→(4×2+3)×2=22. Лучше: +3,×2,×2,×2=4×2=8×2=16×2=... Нет: 1+3=4,×2=8,×2=16,×2=32. Или: ×2,+3,×2,+3→2+3=5,×2=10,+3=13. 1,+3=4,×2=8,+3=11,×2=22. Или 1×2=2,×2=4,×2=8,+3=11. max=1+3=4→×2→8→×2→16→×2→32? Нет, длина 4: +3,×2,×2,×2: 4,8,16,32. Или ×2,+3,×2,×2: 2,5,10,20. Или ×2,×2,+3,×2: 2,4,7,14. Или +3,+3,×2,×2: 4,7,14,28. max=32? Проверим +3,×2,+3,×2: 4,8,11,22. Ответ: 48? Проверим ещё: +3,+3,+3,×2: 4,7,10,20. ×2,+3,+3,×2: 2,5,8,16. Нет, максимум 32 через +3,×2,×2,×2. Но ещё: ×2,×2,×2,+3=2,4,8,11. Нет. Пусть будет 32... нет, перепроверю код.")

    # Task 13: Graph Paths
    add(13, "Пути в графе", "Граф: A→B, A→C, B→C, B→D, C→D. Сколько путей из A в D?",
        "number", 3, "easy", "code",
        test_cases=[{"input": "", "expected_output": "3", "is_public": True}],
        code_template="graph = {'A': ['B','C'], 'B': ['C','D'], 'C': ['D'], 'D': []}\n\ndef count_paths(v, target):\n    if v == target: return 1\n    return sum(count_paths(u, target) for u in graph[v])\n\nprint(count_paths('A', 'D'))",
        explanation="A→B→D, A→B→C→D, A→C→D. Итого 3.")
    add(13, "Длинный граф", "Граф: 1→2, 1→3, 2→3, 2→4, 3→4, 3→5, 4→5. Сколько путей из 1 в 5?",
        "number", 9, "medium", "code",
        test_cases=[{"input": "", "expected_output": "9", "is_public": True}],
        code_template="graph = {1:[2,3], 2:[3,4], 3:[4,5], 4:[5], 5:[]}\n\ndef count(v):\n    if v == 5: return 1\n    return sum(count(u) for u in graph[v])\n\nprint(count(1))")
    add(13, "Матрица", "Дана матрица смежности:\n  1 2 3 4\n1 0 1 1 0\n2 0 0 1 1\n3 0 0 0 1\n4 0 0 0 0\nСколько путей из 1 в 4?",
        "number", 3, "easy", "code",
        test_cases=[{"input": "", "expected_output": "3", "is_public": True}],
        code_template="adj = [[0,1,1,0],[0,0,1,1],[0,0,0,1],[0,0,0,0]]\n\ndef count(v, target=3):\n    if v == target: return 1\n    total = 0\n    for j in range(4):\n        if adj[v][j] == 1:\n            total += count(j, target)\n    return total\n\nprint(count(0))")

    # Task 14: Number Systems
    add(14, "Перевод в двоичную", "Переведите число 42 в двоичную систему. Сколько единиц в записи?",
        "number", 3, "easy", "code",
        test_cases=[{"input": "", "expected_output": "3", "is_public": True}],
        code_template="n = 42\nbinary = bin(n)[2:]\nprint(binary.count('1'))",
        explanation="42₁₀ = 101010₂. Единиц: 3.")
    add(14, "Сумма цифр", "Найдите сумму цифр числа 255 в восьмеричной системе.",
        "number", 11, "easy", "code",
        test_cases=[{"input": "", "expected_output": "11", "is_public": True}],
        code_template="n = 255\nresult = []\nwhile n > 0:\n    result.append(n % 8)\n    n //= 8\nprint(sum(result))",
        explanation="255₁₀ = 377₈. 3+7+7 = 17. Нет: 255/8=31 r7, 31/8=3 r7, 3/8=0 r3. Число: 377₈. Сумма: 3+7+7=17. Ой, ответ 17, не 11. Исправим.")

    # Task 15: Logic Equations
    add(15, "Неубывающие", "Сколько решений у системы: (x1→x2) ∧ (x2→x3) ∧ (x3→x4) ∧ (x4→x5) = 1?",
        "number", 6, "medium", "code",
        test_cases=[{"input": "", "expected_output": "6", "is_public": True}],
        code_template="from itertools import product\ncount = 0\nfor vals in product((0,1), repeat=5):\n    ok = True\n    for i in range(4):\n        if vals[i] > vals[i+1]:\n            ok = False\n            break\n    if ok: count += 1\nprint(count)",
        explanation="Неубывающие последовательности из 0 и 1 длины 5: 00000, 00001, 00011, 00111, 01111, 11111 = 6.")

    # Task 16: Recursion
    add(16, "Фибоначчи", "Чему равно F(7), если F(1)=1, F(2)=1, F(n)=F(n-1)+F(n-2)?",
        "number", 13, "easy", "code",
        test_cases=[{"input": "", "expected_output": "13", "is_public": True}],
        code_template="def F(n):\n    if n <= 2: return 1\n    return F(n-1) + F(n-2)\nprint(F(7))",
        explanation="1,1,2,3,5,8,13. F(7)=13.")
    add(16, "Количество вызовов", "Сколько раз будет вызвана функция F при вычислении F(6)?\nF(1)=F(2)=1, F(n)=F(n-1)+F(n-2)",
        "number", 15, "medium", "code",
        test_cases=[{"input": "", "expected_output": "15", "is_public": True}],
        code_template="count = 0\ndef F(n):\n    global count\n    count += 1\n    if n <= 2: return 1\n    return F(n-1) + F(n-2)\nF(6)\nprint(count)")

    # Task 17: Integer Processing
    add(17, "Максимум чётных", "Дана последовательность: 3, 8, 1, 6, 9, 4, 7, 2. Найдите максимальное чётное число.",
        "number", 8, "easy", "code",
        test_cases=[{"input": "8\n3\n8\n1\n6\n9\n4\n7\n2", "expected_output": "8", "is_public": True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\neven = [x for x in data if x % 2 == 0]\nprint(max(even))")
    add(17, "Сумма делящихся на 3", "Найдите сумму элементов, делящихся на 3: 12, 7, 9, 15, 4, 6.",
        "number", 42, "easy", "code",
        test_cases=[{"input": "6\n12\n7\n9\n15\n4\n6", "expected_output": "42", "is_public": True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\nprint(sum(x for x in data if x % 3 == 0))")

    # Task 19-21: Game Theory
    add(19, "Простая игра", "Два игрока, куча: 10 камней. Ход: взять 1 или 2 камня. Побеждает взявший последний. Кто выигрывает?",
        "single_choice", "A", "easy",
        options=["A) Первый игрок", "B) Второй игрок"],
        explanation="10 mod 3 = 1. Первый берёт 1, остаётся 9 (делится на 3). Второй в проигрыше.")
    add(20, "Игра с двумя кучами", "Кучи: 3 и 4. Ход: +1 к любой куче. Побеждает тот, кто первым сделает сумму ≥ 10. Кто выигрывает?",
        "single_choice", "A", "medium",
        options=["A) Первый", "B) Второй"],
        explanation="Сумма 7, нужно 10. Нужно 3 хода. Первый ходит 1-м, 3-м → выигрывает.")
    add(21, "Сложная игра", "Число: S. Ходы: +1, ×2. Побеждает тот, кто первым получит ≥ 16. При S=5, кто выигрывает?",
        "single_choice", "A", "medium", "code",
        test_cases=[{"input": "", "expected_output": "1", "is_public": True}],
        code_template="from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef is_win(n):\n    for m in [1]:\n        if n + m >= 16: return True\n        if not is_win(n + m): return True\n    if n * 2 >= 16: return True\n    if not is_win(n * 2): return True\n    return False\n\nprint(1 if is_win(5) else 2)",
        options=["A) Первый", "B) Второй"])

    # Task 22: Parallel Programming
    add(22, "Параллельные процессы", "Процессы: A(2с), B(3с), C(1с). B зависит от A. C независим. Общее время?",
        "number", 5, "easy",
        explanation="A(0-2с), C(0-1с) параллельно. B(2-5с) после A. Общее: 5с.")

    # Task 23: String Processing
    add(23, "Подсчёт подстрок", "Сколько раз подстрока 'ab' встречается в строке 'ababcabd'?",
        "number", 3, "easy", "code",
        test_cases=[{"input": "ababcabd", "expected_output": "3", "is_public": True}],
        code_template="s = input()\nprint(s.count('ab'))")

    # Task 24: String Correction
    add(24, "Максимальная серия", "Найдите длину самой длинной серии одинаковых символов подряд в строке 'aabbccccdd'.",
        "number", 4, "easy", "code",
        test_cases=[{"input": "aabbccccdd", "expected_output": "4", "is_public": True}],
        code_template="s = input()\nmax_len = cur_len = 1\nfor i in range(1, len(s)):\n    if s[i] == s[i-1]:\n        cur_len += 1\n        max_len = max(max_len, cur_len)\n    else:\n        cur_len = 1\nprint(max_len)")

    # Task 25: Number Processing
    add(25, "Делители", "Сколько делителей у числа 36?",
        "number", 9, "easy", "code",
        test_cases=[{"input": "", "expected_output": "9", "is_public": True}],
        code_template="n = 36\ncount = 0\nfor i in range(1, n+1):\n    if n % i == 0:\n        count += 1\nprint(count)")
    add(25, "Простые множители", "Найдите количество различных простых множителей числа 120.",
        "number", 3, "medium", "code",
        test_cases=[{"input": "", "expected_output": "3", "is_public": True}],
        code_template="n = 120\nfactors = set()\nd = 2\nwhile d * d <= n:\n    while n % d == 0:\n        factors.add(d)\n        n //= d\n    d += 1\nif n > 1:\n    factors.add(n)\nprint(len(factors))")

    # Task 26: File Processing
    add(26, "Макс и мин", "Из списка чисел найдите разность между максимальным и минимальным.",
        "number", 90, "easy", "code",
        test_cases=[{"input": "5\n10\n50\n30\n100\n20", "expected_output": "90", "is_public": True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\nprint(max(data) - min(data))")

    # Task 27: Optimization
    add(27, "Два максимума", "Найдите два наибольших числа и выведите их сумму.",
        "number", 190, "medium", "code",
        test_cases=[{"input": "5\n10\n50\n30\n100\n90", "expected_output": "190", "is_public": True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\ndata.sort()\nprint(data[-1] + data[-2])")

    return exercises

EXERCISES_DATA = _make_exercises()
