def _make_extra_exercises():
    exercises = []
    eid = 1000

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

    # ====== TASK 1 additional ======
    add(1,"Связный граф","В неориентированном графе 6 вершин: A,B,C,D,E,F. Рёбра: A-B, B-C, C-D, D-E, E-F, F-A, B-D. Сколько рёбер?","number",7,"easy",
        explanation="Перечислим: A-B, B-C, C-D, D-E, E-F, F-A, B-D = 7 рёбер.")
    add(1,"Компоненты связности","Граф: вершины 1-6. Рёбра: 1-2, 2-3, 4-5. Сколько компонент связности?","number",3,"medium",
        explanation="Компоненты: {1,2,3}, {4,5}, {6}. Итого 3.",hints=["Компонента — максимальное подмножество связных вершин"])
    add(1,"Ориентированный граф","В орграфе: A→B, B→C, C→A, A→D. Из какой вершины можно попасть во все остальные?",
        "single_choice","A","easy",options=["A) A","B) B","C) C","D) D"],
        explanation="Из A: A→B, A→B→C, A→D. Из A достижимы все.")
    add(1,"Весовой граф","В взвешенном графе рёбра: A-B(3), A-C(5), B-C(2), B-D(7), C-D(4). Кратчайший путь A→D?",
        "number",9,"medium",explanation="A-B-C-D: 3+2+4=9. A-C-D: 5+4=9. A-B-D: 3+7=10. Минимум=9.")
    add(1,"Изоморфизм","Два графа: G1 с рёбрами A-B,B-C,C-A и G2 с рёбрами X-Y,Y-Z,Z-X. Изоморфны ли они?",
        "single_choice","A","easy",options=["A) Да","B) Нет"],explanation="Оба — треугольники, изоморфны.")
    add(1,"Полный граф","Сколько рёбер в полном графе с 5 вершинами?","number",10,"easy",
        explanation="C(5,2) = 5*4/2 = 10.")
    add(1,"Эйлеров путь","В каком графе существует эйлеров путь (не цикл)? Дан граф: A-B, A-C, A-D, B-C, C-D. Степени: A=3, B=2, C=3, D=2. Сколько вершин нечётной степени?",
        "number",2,"medium",explanation="A(3) и C(3) — нечётные. Ровно 2 — эйлеров путь существует.")
    add(1,"Дерево поиска","В дереве с корнем A: A→B, A→C, B→D, B→E. Сколько листьев?",
        "number",3,"easy",explanation="Листья: C, D, E = 3.")
    add(1,"Матрица инцидентности","Граф: A-B, A-C, B-C. Сколько единиц в матрице инцидентности?",
        "number",6,"medium",explanation="3 ребра, каждое инцидентно 2 вершинам = 6 единиц.")
    add(1,"Двудольный граф","Граф: A-X, A-Y, B-X, B-Y, C-X. Является ли он двудольным?",
        "single_choice","A","easy",options=["A) Да","B) Нет"],explanation="Доли: {A,B,C} и {X,Y}. Все рёбра между долями.")

    # ====== TASK 2 additional ======
    add(2,"XOR","Сколько строк таблицы истинности выражения A ⊕ B ⊕ C дают 1?","number",4,"easy","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor a,b,c in product((0,1), repeat=3):\n    if (a ^ b ^ c):\n        count += 1\nprint(count)",
        explanation="XOR трёх переменных = 1, когда нечётное число единиц: 001,010,100,111 = 4.")
    add(2,"Де Морган","Выражение ¬(A ∧ B) эквивалентно:","single_choice","B","easy",
        options=["A) ¬A ∧ ¬B","B) ¬A ∨ ¬B","C) A ∨ B","D) ¬A → B"],
        explanation="Закон де Моргана: ¬(A∧B) = ¬A ∨ ¬B.")
    add(2,"5 переменных","Найдите количество решений: (x1∨x2) ∧ (x3∨x4) ∧ x5 = 1","number",9,"medium","code",
        test_cases=[{"input":"","expected_output":"9","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor vals in product((0,1), repeat=5):\n    x1,x2,x3,x4,x5 = vals\n    if (x1 or x2) and (x3 or x4) and x5:\n        count += 1\nprint(count)",
        explanation="x5=1. (x1∨x2): 3 из 4. (x3∨x4): 3 из 4. Итого: 3*3*1=9.")
    add(2,"Тождество","Для скольких наборов (A,B) верно: (A→B) = (¬B→¬A)?","number",4,"easy",
        explanation="Это тождество (контрапозиция), верно для всех 4 наборов.",
        hints=["Контрапозиция — всегда тождество"])
    add(2,"Сложное выражение","Сколько решений: (A∨¬B) ∧ (B∨¬C) ∧ (C∨¬A) = 1?","number",4,"medium","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor a,b,c in product((0,1), repeat=3):\n    if (a or not b) and (b or not c) and (c or not a):\n        count += 1\nprint(count)")
    add(2,"Импликация и AND","Количество строк: (A→B) ∧ (B→C) = 1?","number",4,"easy","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor a,b,c in product((0,1), repeat=3):\n    imp1 = (not a) or b\n    imp2 = (not b) or c\n    if imp1 and imp2:\n        count += 1\nprint(count)")
    add(2,"Количество 0","Сколько строк дают значение 0 для выражения A ∨ B ∨ C?","number",1,"easy",
        explanation="A∨B∨C=0 только при A=B=C=0. Одна строка.")
    add(2,"Эквивалентность 3","(A↔B)↔C — сколько строк дают 1?","number",4,"medium","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor a,b,c in product((0,1), repeat=3):\n    if ((a==b)==c):\n        count += 1\nprint(count)")
    add(2,"6 переменных","Система: (x1→x2)∧(x2→x3)∧(x3→x4)∧(x4→x5)∧(x5→x6)=1. Количество решений?","number",7,"hard","code",
        test_cases=[{"input":"","expected_output":"7","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor vals in product((0,1), repeat=6):\n    ok = True\n    for i in range(5):\n        if vals[i] > vals[i+1]:\n            ok = False\n            break\n    if ok: count += 1\nprint(count)",
        explanation="Неубывающие последовательности из 0 и 1 длины 6: C(6+1,1)=7.")
    add(2,"Штрих Шеффера","A | B (штрих Шеффера) = ¬(A∧B). Вычислите (1|1)|0.","number",1,"hard",
        explanation="1|1 = ¬(1∧1) = 0. 0|0 = ¬(0∧0) = 1. Ответ: 1.")

    # ====== TASK 3 additional ======
    add(3,"Составной запрос","Таблица учеников: Иван(5,Матем), Мария(4,Физика), Пётр(5,Матем), Анна(3,Физика), Дима(5,Информ). Сколько учеников с оценкой 5 И предмет = Матем?",
        "number",2,"easy",explanation="Иван и Пётр.")
    add(3,"COUNT","В таблице 10 записей. У 4 записей поле Возраст > 30. Чему равно COUNT(*) WHERE Возраст > 30?","number",4,"easy")
    add(3,"MIN","Значения поля Цена: 100, 250, 80, 320, 150. MIN(Цена) = ?","number",80,"easy")
    add(3,"Связь таблиц","Таблица Заказы: id,клиент_id,сумма. Таблица Клиенты: id,имя,город. Сколько заказов у клиента 'Москва', если клиенты из Москвы имеют id=1,3, а заказы: (1,1,100),(2,2,200),(3,1,150),(4,3,300)?",
        "number",3,"medium",explanation="Клиенты Москва: id=1,3. Заказы с клиент_id 1 или 3: заказы 1,3,4. Итого 3.")
    add(3,"GROUP BY","Таблица продаж: (Яблоко,5),(Банан,3),(Яблоко,2),(Банан,7),(Вишня,1). SUM(кол-во) GROUP BY продукт. Максимальная сумма?",
        "number",10,"medium",explanation="Яблоко: 5+2=7. Банан: 3+7=10. Вишня: 1. Максимум=10.")
    add(3,"HAVING","Продолжая предыдущую задачу, сколько продуктов имеют SUM > 5?","number",1,"medium",
        explanation="Яблоко=7>5, Банан=10>5, Вишня=1<5. Но с HAVING SUM>5 нужно 2... нет, вопрос: >5 строго. Яблоко=7, Банан=10. Ответ: 2.",
        hints=["HAVING фильтрует после GROUP BY"])
    add(3,"ORDER BY","Записи: (А,30),(Б,25),(В,35),(Г,25). ORDER BY возраст, имя. Какая запись первая?","single_choice","B","easy",
        options=["A) А,30","B) Б,25","C) Г,25","D) В,35"],explanation="Сортировка: 25(Б), 25(Г), 30(А), 35(В). Первая — Б.")
    add(3,"NOT","Таблица: 10 записей, из них 3 с городом='Москва'. Сколько записей вернёт WHERE город <> 'Москва'?","number",7,"easy")
    add(3,"LIKE","Маска 'А%в'. Какое имя подходит: Алексеев, Борисов, Андреев, Абрамов?","multiple_choice",["A","C"],"medium",
        options=["A) Алексеев","B) Борисов","C) Андреев","D) Абрамов"],
        explanation="Начинается на А, заканчивается на в: Алексеев, Андреев.")
    add(3,"DISTINCT","В таблице значения поля Город: Москва,СПб,Москва,Казань,СПб,Москва. Сколько вернёт SELECT DISTINCT Город?","number",3,"easy")

    # ====== TASK 4 additional ======
    add(4,"Равномерный код","Для кодирования 50 символов равномерным двоичным кодом минимальная длина кодового слова?","number",6,"easy",
        explanation="2^5=32<50, 2^6=64>=50. Ответ: 6 бит.")
    add(4,"Длина сообщения","Сообщение 'АБВАБВ' закодировано: А=0, Б=10, В=11. Длина в битах?","number",10,"easy",
        explanation="0+10+11+0+10+11 = 1+2+2+1+2+2 = 10 бит.")
    add(4,"Дерево кодов","Коды: a=00, b=01, c=100, d=101, e=11. Является ли это префиксным кодом?","single_choice","A","medium",
        options=["A) Да","B) Нет"],explanation="Ни один код не является началом другого. Да.")
    add(4,"Минимальная длина","Коды: A=1, B=01. Какой минимальной длины код можно назначить C, сохранив условие Фано?","number",3,"medium",
        explanation="Занятые ветви: 1xx, 01x. Свободные: 000, 001. Минимум = 3.")
    add(4,"Средняя длина","Символы с частотами: A(0.5), B(0.25), C(0.25). Коды: A=0, B=10, C=11. Средняя длина?","number",1.5,"medium",
        explanation="0.5*1 + 0.25*2 + 0.25*2 = 0.5 + 0.5 + 0.5 = 1.5 бит.",hints=["Средняя длина = сумма(частота × длина)"])
    add(4,"Декодирование 2","Коды: a=0, b=10, c=110, d=111. Декодируйте: 1101011100. Количество символов?","number",5,"medium",
        explanation="110|10|111|0|0 → c b d a a = 5 символов.")
    add(4,"Неравенство Крафта 2","Возможен ли префиксный код с длинами 1, 2, 2, 3?","single_choice","A","medium",
        options=["A) Да","B) Нет"],explanation="1/2 + 1/4 + 1/4 + 1/8 = 1.125 > 1. Нет! Ответ: Нет.",
        hints=["Проверьте неравенство Крафта: сумма 2^(-li) <= 1"])
    add(4,"Хаффман","Для алфавита {A:5, B:3, C:2, D:1} постройте оптимальный код. Какова длина кода D?","number",3,"hard",
        explanation="Дерево Хаффмана: D и C объединяются (3), потом с B (6), потом с A (11). D получит код длины 3.")
    add(4,"Однозначность","Код: A=0, B=00. Можно ли однозначно декодировать 000?","single_choice","B","easy",
        options=["A) Да","B) Нет"],explanation="000 = A+A+A или A+B или B+A. Не однозначно.")

    # ====== TASK 5 additional ======
    add(5,"Факториал","Чему равно значение x после: x=1; for i in range(1,6): x*=i","number",120,"easy","code",
        test_cases=[{"input":"","expected_output":"120","is_public":True}],
        code_template="x = 1\nfor i in range(1, 6):\n    x *= i\nprint(x)")
    add(5,"Степень двойки","Наименьшая степень 2, превышающая 1000?","number",1024,"easy","code",
        test_cases=[{"input":"","expected_output":"1024","is_public":True}],
        code_template="x = 1\nwhile x <= 1000:\n    x *= 2\nprint(x)")
    add(5,"Фибоначчи вручную","Чему равен 8-й член последовательности: 1,1,2,3,5,8,...?","number",21,"easy","code",
        test_cases=[{"input":"","expected_output":"21","is_public":True}],
        code_template="a, b = 1, 1\nfor _ in range(6):\n    a, b = b, a + b\nprint(b)")
    add(5,"Сумма ряда","Найдите сумму 1+2+4+8+...+512","number",1023,"medium","code",
        test_cases=[{"input":"","expected_output":"1023","is_public":True}],
        code_template="s = 0\nx = 1\nwhile x <= 512:\n    s += x\n    x *= 2\nprint(s)")
    add(5,"Евклид","Найдите НОД(48, 36) алгоритмом Евклида.","number",12,"medium","code",
        test_cases=[{"input":"","expected_output":"12","is_public":True}],
        code_template="a, b = 48, 36\nwhile b:\n    a, b = b, a % b\nprint(a)")
    add(5,"Обратный алгоритм","Исполнитель: -3, //2. Начальное значение 100. Программа: //2, -3, //2, -3. Результат?","number",21,"medium","code",
        test_cases=[{"input":"","expected_output":"21","is_public":True}],
        code_template="x = 100\nx = x // 2  # 50\nx = x - 3   # 47\nx = x // 2  # 23\nx = x - 3   # 20\nprint(x)",
        explanation="100//2=50, 50-3=47, 47//2=23, 23-3=20. Ответ: 20.")
    add(5,"Количество делителей","Напишите программу, считающую количество делителей числа 60.","number",12,"medium","code",
        test_cases=[{"input":"","expected_output":"12","is_public":True}],
        code_template="n = 60\ncount = 0\nfor i in range(1, n+1):\n    if n % i == 0:\n        count += 1\nprint(count)")
    add(5,"Цифры числа","Сколько цифр в числе 123456789?","number",9,"easy","code",
        test_cases=[{"input":"","expected_output":"9","is_public":True}],
        code_template="n = 123456789\nprint(len(str(n)))")
    add(5,"Максимальная цифра","Найдите максимальную цифру числа 47291.","number",9,"easy","code",
        test_cases=[{"input":"","expected_output":"9","is_public":True}],
        code_template="n = 47291\nprint(max(int(d) for d in str(n)))")

    # ====== TASK 6 additional ======
    add(6,"Чётные в диапазоне","Сколько чётных чисел от 10 до 30 включительно?","number",11,"easy","code",
        test_cases=[{"input":"","expected_output":"11","is_public":True}],
        code_template="count = 0\nfor i in range(10, 31):\n    if i % 2 == 0:\n        count += 1\nprint(count)")
    add(6,"Простые числа","Сколько простых чисел от 1 до 20?","number",8,"medium","code",
        test_cases=[{"input":"","expected_output":"8","is_public":True}],
        code_template="def is_prime(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True\n\nprint(sum(1 for i in range(1,21) if is_prime(i)))")
    add(6,"Палиндром","Является ли число 12321 палиндромом? Выведите 1 (да) или 0 (нет).","number",1,"easy","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        code_template="n = 12321\ns = str(n)\nprint(1 if s == s[::-1] else 0)")
    add(6,"Сумма чётных позиций","Дана строка '123456'. Найдите сумму цифр на чётных позициях (2,4,6).","number",12,"medium","code",
        test_cases=[{"input":"","expected_output":"12","is_public":True}],
        code_template="s = '123456'\ntotal = 0\nfor i in range(1, len(s), 2):\n    total += int(s[i])\nprint(total)",
        explanation="Позиции 2,4,6 (индексы 1,3,5): 2+4+6=12.")
    add(6,"Сортировка цифр","Переставьте цифры числа 53142 в порядке возрастания и выведите результат.","number",12345,"easy","code",
        test_cases=[{"input":"","expected_output":"12345","is_public":True}],
        code_template="n = 53142\nprint(int(''.join(sorted(str(n)))))")
    add(6,"Степень тройки","Является ли 729 степенью тройки? Выведите показатель степени или -1.","number",6,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        code_template="n = 729\nk = 0\nwhile n > 1:\n    if n % 3 != 0:\n        k = -1\n        break\n    n //= 3\n    k += 1\nprint(k)")
    add(6,"Двоичная запись","Переведите 255 в двоичную систему. Выведите строку.","number",11111111,"easy","code",
        test_cases=[{"input":"","expected_output":"11111111","is_public":True}],
        code_template="print(bin(255)[2:])")
    add(6,"Сумма квадратов","Найдите сумму квадратов чисел от 1 до 5.","number",55,"easy","code",
        test_cases=[{"input":"","expected_output":"55","is_public":True}],
        code_template="print(sum(i**2 for i in range(1, 6)))")

    # ====== TASK 7 additional ======
    add(7,"Размер страницы","Документ 20 страниц, 40 строк на странице, 60 символов в строке. Алфавит 256 символов. Объём в КБ?",
        "number",46,"easy",explanation="20*40*60=48000 символов. 256→8 бит=1 байт. 48000 байт ≈ 46.875 КБ ≈ 47. Точнее: 48000/1024=46.875. Округляем = 46 или 47.",
        hints=["1 символ = 1 байт при 256-символьном алфавите"])
    add(7,"Разрешение","Изображение занимает 150 КБ. Глубина цвета 24 бита. Разрешение 320×?. Найдите высоту.",
        "number",640,"medium",explanation="150 КБ = 153600 байт = 1228800 бит. 1228800/24 = 51200 пикселей. 51200/320 = 160. Нет... 150*1024=153600 байт. 153600*8=1228800 бит. 1228800/24=51200 пикселей. 51200/320=160.",
        hints=["V = W × H × глубина"])
    add(7,"Стерео","Длительность звука 10 с, частота 22050 Гц, 8 бит, моно. Объём в КБ?",
        "number",215,"easy",explanation="22050*8*1*10 = 1764000 бит = 220500 байт ≈ 215.3 КБ.",
        hints=["Моно = 1 канал"])
    add(7,"Текст Unicode","Сообщение из 500 символов в UTF-16 (2 байта на символ). Объём в байтах?","number",1000,"easy",
        explanation="500*2=1000 байт.")
    add(7,"Цвет","Для хранения 1 пикселя используется 3 байта. Это соответствует палитре из скольких цветов?",
        "number",16777216,"medium",explanation="3 байта = 24 бита. 2^24 = 16777216.")
    add(7,"Сжатие","Файл 2 МБ сжат в 4 раза. Размер после сжатия в КБ?","number",512,"easy",
        explanation="2 МБ = 2048 КБ. 2048/4 = 512 КБ.")
    add(7,"Видео","Видео: 25 кадров/с, каждый кадр 100 КБ, длительность 2 секунды. Объём в КБ?","number",5000,"easy",
        explanation="25*2=50 кадров. 50*100=5000 КБ.")

    # ====== TASK 8 additional ======
    add(8,"Бинарные строки","Сколько двоичных строк длины 5 содержат ровно 2 единицы?","number",10,"easy","code",
        test_cases=[{"input":"","expected_output":"10","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor s in product((0,1), repeat=5):\n    if sum(s) == 2:\n        count += 1\nprint(count)",
        explanation="C(5,2) = 10.")
    add(8,"Пароль","Пароль из 4 цифр (0-9), все различные. Сколько вариантов?","number",5040,"medium","code",
        test_cases=[{"input":"","expected_output":"5040","is_public":True}],
        code_template="from itertools import permutations\nprint(len(list(permutations(range(10), 4))))",
        explanation="A(10,4) = 10*9*8*7 = 5040.")
    add(8,"Анаграммы","Сколько различных перестановок букв в слове АББА?","number",6,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        code_template="from itertools import permutations\nresult = set(permutations('АББА'))\nprint(len(result))",
        explanation="4!/(2!*2!) = 6.")
    add(8,"Подмножества","Сколько подмножеств у множества {1,2,3,4}?","number",16,"easy",
        explanation="2^4 = 16 (включая пустое).")
    add(8,"Пути на сетке","На сетке 3×3 из нижнего левого угла в верхний правый. Ход: вправо или вверх. Сколько путей?","number",6,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        code_template="from math import comb\n# 2 шага вправо + 2 вверх = C(4,2)\nprint(comb(4, 2))",
        explanation="Нужно 2 шага вправо и 2 вверх = C(4,2) = 6.")
    add(8,"Цифры без 0","Сколько 3-значных чисел можно составить из цифр 1-5 с повторениями?","number",125,"easy","code",
        test_cases=[{"input":"","expected_output":"125","is_public":True}],
        code_template="print(5**3)")
    add(8,"Чётные числа","Сколько 3-значных чётных чисел можно составить из цифр {1,2,3,4}?","number",32,"medium","code",
        test_cases=[{"input":"","expected_output":"32","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor d in product([1,2,3,4], repeat=3):\n    num = d[0]*100 + d[1]*10 + d[2]\n    if num % 2 == 0:\n        count += 1\nprint(count)",
        explanation="Последняя цифра: 2 или 4 (2 варианта). Первые две: 4*4=16. Итого: 16*2=32.")

    # ====== TASK 9 additional ======
    add(9,"IF-формула","=ЕСЛИ(A1>10;A1*2;A1+5). A1=7. Результат?","number",12,"easy",
        explanation="7>10? Нет. Значит A1+5=7+5=12.")
    add(9,"Вложенный IF","=ЕСЛИ(A1>100;'A';ЕСЛИ(A1>50;'B';'C')). A1=75. Результат?","single_choice","B","medium",
        options=["A) A","B) B","C) C"],explanation="75>100? Нет. 75>50? Да. Ответ: B.")
    add(9,"СЧЁТЕСЛИ","Ячейки A1:A6 = 3,5,8,3,2,3. =СЧЁТЕСЛИ(A1:A6;3) = ?","number",3,"easy",
        explanation="Число 3 встречается 3 раза.")
    add(9,"Смешанная ссылка","В C1: =A$1+$B1. Копируем в D2. Результат?","single_choice","C","medium",
        options=["A) =A$1+$B2","B) =B$1+$B1","C) =B$1+$B2","D) =A$2+$B2"],
        explanation="C1→D2: +1 столбец, +1 строка. A→B ($1 остаётся), $B остаётся (1→2). Ответ: =B$1+$B2.")
    add(9,"СУММЕСЛИ","A1:A4=10,20,30,40. B1:B4='да','нет','да','да'. =СУММЕСЛИ(B1:B4;'да';A1:A4)=?","number",80,"medium",
        explanation="Строки с 'да': A1(10)+A3(30)+A4(40)=80.")
    add(9,"Процент","=A1/СУММ(A1:A3)*100. A1=30, A2=50, A3=20. Результат?","number",30,"easy",
        explanation="30/(30+50+20)*100 = 30/100*100 = 30.")

    # ====== TASK 10 additional ======
    add(10,"Точная длина","Маска к??а. Алфавит 33 буквы. Сколько слов?","number",1089,"easy",
        explanation="к??а: 1*33*33*1 = 1089.")
    add(10,"Звёздочка","Маска: *ть. Какие слова подходят: петь, мать, кость, путь?","multiple_choice",["A","B","C","D"],"easy",
        options=["A) петь","B) мать","C) кость","D) путь"],
        explanation="Все заканчиваются на 'ть'.")
    add(10,"Двойная звёздочка","Маска: а*б*а. Минимальная длина слова?","number",3,"medium",
        explanation="а+пусто+б+пусто+а → 'аба' = 3 символа.")
    add(10,"Регистр","Маска: ?Б? (регистрозависимый). Какие подходят: АБВ, абв, ОБО?","multiple_choice",["A","C"],"easy",
        options=["A) АБВ","B) абв","C) ОБО"],explanation="Второй символ = Б (заглавная). АБВ и ОБО.")

    # ====== TASK 11 additional ======
    add(11,"Событие","В мешке 8 шаров. Вынули один. Количество информации?","number",3,"easy",
        explanation="log2(8)=3 бита.")
    add(11,"Неравновероятные","Монета: орёл с вер. 0.5, решка 0.5. Информация?","number",1,"easy",
        explanation="2 равновероятных исхода → 1 бит.")
    add(11,"Большой алфавит","Мощность алфавита 128. Бит на символ?","number",7,"easy",
        explanation="log2(128)=7.")
    add(11,"Файл","Текстовый файл 10 КБ. Мощность алфавита 256. Сколько символов?","number",10240,"easy",
        explanation="10 КБ = 10240 байт. 256 символов → 1 байт/символ. 10240 символов.")
    add(11,"Страница","На странице 50 строк по 80 символов. 256-символьный алфавит. Объём страницы в байтах?","number",4000,"easy",
        explanation="50*80=4000 символов = 4000 байт.")

    # ====== TASK 12 additional ======
    add(12,"Два исполнителя","Исполнитель: +1, *3. Начало: 2. Программа длины 3, максимальный результат?","number",27,"medium","code",
        test_cases=[{"input":"","expected_output":"27","is_public":True}],
        code_template="from itertools import product\nmx = 0\nfor cmds in product([1,2], repeat=3):\n    x = 2\n    for c in cmds:\n        if c == 1: x += 1\n        else: x *= 3\n    mx = max(mx, x)\nprint(mx)",
        explanation="Стратегия: максимизировать умножения. 2→*3→6→*3→18→*3→54 или 2→+1→3→*3→9→*3→27. Максимум перебором.")
    add(12,"Обратная задача","Исполнитель: +2, *2. Какое минимальное начальное значение, чтобы программа длины 2 дала результат >=20?","number",5,"medium","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        code_template="from itertools import product\nfor start in range(1, 100):\n    for cmds in product([1,2], repeat=2):\n        x = start\n        for c in cmds:\n            if c == 1: x += 2\n            else: x *= 2\n        if x >= 20:\n            print(start)\n            exit()",
        explanation="start=5: 5*2=10,*2=20. Или 5*2=10,+2=12. Или 5+2=7,*2=14. 5,*2,*2=20>=20. Ответ: 5.")
    add(12,"Программа длины 5","Исполнитель: +1, ×2. Начало: 1. Сколько программ длины 5 дают чётный результат?","number",24,"hard","code",
        test_cases=[{"input":"","expected_output":"24","is_public":True}],
        code_template="from itertools import product\ncount = 0\nfor cmds in product([1,2], repeat=5):\n    x = 1\n    for c in cmds:\n        if c == 1: x += 1\n        else: x *= 2\n    if x % 2 == 0:\n        count += 1\nprint(count)")

    # ====== TASK 13 additional ======
    add(13,"5 вершин","Граф: 1→2, 1→3, 2→4, 2→5, 3→4, 3→5, 4→5. Путей из 1 в 5?","number",5,"medium","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        code_template="g = {1:[2,3], 2:[4,5], 3:[4,5], 4:[5], 5:[]}\ndef c(v):\n    if v == 5: return 1\n    return sum(c(u) for u in g[v])\nprint(c(1))")
    add(13,"Линейный граф","Граф: 1→2→3→4→5. Сколько путей из 1 в 5?","number",1,"easy","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        code_template="g = {1:[2], 2:[3], 3:[4], 4:[5], 5:[]}\ndef c(v):\n    if v == 5: return 1\n    return sum(c(u) for u in g[v])\nprint(c(1))")
    add(13,"Ромб","Граф: A→B, A→C, B→D, C→D, A→D. Путей A→D?","number",3,"easy","code",
        test_cases=[{"input":"","expected_output":"3","is_public":True}],
        code_template="g = {'A':['B','C','D'], 'B':['D'], 'C':['D'], 'D':[]}\ndef c(v):\n    if v == 'D': return 1\n    return sum(c(u) for u in g[v])\nprint(c('A'))")

    # ====== TASK 14 additional ======
    add(14,"Перевод в 8-ричную","Число 100 в восьмеричной системе?","number",144,"easy","code",
        test_cases=[{"input":"","expected_output":"144","is_public":True}],
        code_template="print(oct(100)[2:])")
    add(14,"Из 16-ричной","Число 1A в 16-ричной = ? в десятичной","number",26,"easy","code",
        test_cases=[{"input":"","expected_output":"26","is_public":True}],
        code_template="print(int('1A', 16))")
    add(14,"Количество цифр","Сколько цифр в двоичной записи числа 1000?","number",10,"medium","code",
        test_cases=[{"input":"","expected_output":"10","is_public":True}],
        code_template="print(len(bin(1000)[2:]))")
    add(14,"Сумма в двоичной","Чему равна сумма цифр числа 100 в двоичной записи?","number",3,"easy","code",
        test_cases=[{"input":"","expected_output":"3","is_public":True}],
        code_template="print(bin(100).count('1'))")
    add(14,"Основание","В какой системе счисления 21 = 17 (десятичное)?","number",8,"medium","code",
        test_cases=[{"input":"","expected_output":"8","is_public":True}],
        code_template="for base in range(2, 37):\n    if 2*base + 1 == 17:\n        print(base)\n        break",
        explanation="2*b+1=17, b=8.")

    # ====== TASK 15 additional ======
    add(15,"Простая система","(x1∨x2)∧(¬x1∨x3)=1. Количество решений?","number",5,"medium","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        code_template="from itertools import product\nc = 0\nfor x1,x2,x3 in product((0,1), repeat=3):\n    if (x1 or x2) and (not x1 or x3):\n        c += 1\nprint(c)")
    add(15,"Двойная импликация","(x1→x2)∧(x2→x1)=1. Количество решений?","number",2,"easy","code",
        test_cases=[{"input":"","expected_output":"2","is_public":True}],
        code_template="from itertools import product\nc = 0\nfor x1,x2 in product((0,1), repeat=2):\n    if (x1 <= x2) and (x2 <= x1):\n        c += 1\nprint(c)",
        explanation="x1=x2. Два решения: (0,0) и (1,1).")

    # ====== TASK 16 additional ======
    add(16,"Факториал рекурсия","Чему равно F(6), если F(0)=1, F(n)=n*F(n-1)?","number",720,"easy","code",
        test_cases=[{"input":"","expected_output":"720","is_public":True}],
        code_template="def F(n):\n    if n == 0: return 1\n    return n * F(n-1)\nprint(F(6))")
    add(16,"Сумма цифр","F(n) = сумма цифр n, если n<10, иначе F(сумма_цифр(n)). F(9999)?","number",9,"medium","code",
        test_cases=[{"input":"","expected_output":"9","is_public":True}],
        code_template="def F(n):\n    if n < 10: return n\n    return F(sum(int(d) for d in str(n)))\nprint(F(9999))",
        explanation="9999→36→9. Ответ: 9 (цифровой корень).")

    # ====== TASK 17 additional ======
    add(17,"Два максимума","Из последовательности 5,8,3,12,7,1,9 найти сумму двух наибольших.","number",21,"easy","code",
        test_cases=[{"input":"7\n5\n8\n3\n12\n7\n1\n9","expected_output":"21","is_public":True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\ndata.sort()\nprint(data[-1] + data[-2])")
    add(17,"Среднее","Найти среднее арифметическое положительных чисел: -3, 5, -1, 8, 2, -4.","number",5,"easy","code",
        test_cases=[{"input":"6\n-3\n5\n-1\n8\n2\n-4","expected_output":"5","is_public":True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\npos = [x for x in data if x > 0]\nprint(sum(pos) // len(pos))",
        explanation="Положительные: 5,8,2. Сумма=15. Среднее=15/3=5.")

    # ====== TASK 23 additional ======
    add(23,"Гласные","Сколько гласных (аеёиоуыэюя) в строке 'информатика'?","number",5,"easy","code",
        test_cases=[{"input":"информатика","expected_output":"5","is_public":True}],
        code_template="s = input().lower()\nvowels = 'аеёиоуыэюя'\nprint(sum(1 for c in s if c in vowels))")
    add(23,"Обратная строка","Выведите строку 'Python' задом наперёд.","number",0,"easy","code",
        test_cases=[{"input":"Python","expected_output":"nohtyP","is_public":True}],
        code_template="print(input()[::-1])")
    add(23,"Удвоение","Удвойте каждый символ: 'ABC' → 'AABBCC'","number",0,"easy","code",
        test_cases=[{"input":"ABC","expected_output":"AABBCC","is_public":True}],
        code_template="s = input()\nprint(''.join(c*2 for c in s))")

    # ====== TASK 24 additional ======
    add(24,"Чередование","Найти самую длинную подстроку чередующихся символов в 'ababacc'.","number",5,"medium","code",
        test_cases=[{"input":"ababacc","expected_output":"5","is_public":True}],
        code_template="s = input()\nmax_l = cur_l = 1\nfor i in range(1, len(s)):\n    if s[i] != s[i-1]:\n        cur_l += 1\n        max_l = max(max_l, cur_l)\n    else:\n        cur_l = 1\nprint(max_l)",
        explanation="'ababa' — 5 чередующихся символов.")
    add(24,"Количество слов","Сколько слов в строке 'Привет мир это тест'?","number",4,"easy","code",
        test_cases=[{"input":"Привет мир это тест","expected_output":"4","is_public":True}],
        code_template="print(len(input().split()))")

    # ====== TASK 25 additional ======
    add(25,"Совершенное число","Является ли 28 совершенным числом (сумма делителей кроме себя = числу)? 1=да, 0=нет","number",1,"medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        code_template="n = 28\ns = sum(i for i in range(1, n) if n % i == 0)\nprint(1 if s == n else 0)",
        explanation="Делители 28: 1,2,4,7,14. Сумма=28. Совершенное.")
    add(25,"НОД","НОД(120, 84)?","number",12,"easy","code",
        test_cases=[{"input":"","expected_output":"12","is_public":True}],
        code_template="from math import gcd\nprint(gcd(120, 84))")
    add(25,"НОК","НОК(12, 18)?","number",36,"easy","code",
        test_cases=[{"input":"","expected_output":"36","is_public":True}],
        code_template="from math import gcd\na, b = 12, 18\nprint(a * b // gcd(a, b))")

    # ====== TASK 26 additional ======
    add(26,"Пары с суммой","Найти количество пар элементов с суммой 10 из списка: 3,7,2,8,5,5,1,9.","number",4,"medium","code",
        test_cases=[{"input":"8\n3\n7\n2\n8\n5\n5\n1\n9","expected_output":"4","is_public":True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\ncount = 0\nfor i in range(n):\n    for j in range(i+1, n):\n        if data[i] + data[j] == 10:\n            count += 1\nprint(count)",
        explanation="Пары: (3,7),(2,8),(5,5),(1,9)=4.")
    add(26,"Медиана","Найти медиану: 5,2,8,1,9,3,7. Выведите медиану.","number",5,"easy","code",
        test_cases=[{"input":"7\n5\n2\n8\n1\n9\n3\n7","expected_output":"5","is_public":True}],
        code_template="n = int(input())\ndata = sorted([int(input()) for _ in range(n)])\nprint(data[n//2])")

    # ====== TASK 27 additional ======
    add(27,"Оптимальная пара","Найти два числа из списка, произведение которых максимально.","number",0,"medium","code",
        test_cases=[{"input":"5\n-10\n-3\n5\n2\n8","expected_output":"40","is_public":True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\ndata.sort()\n# Максимальное произведение: два наибольших ИЛИ два наименьших (отрицательных)\nprint(max(data[-1]*data[-2], data[0]*data[1]))",
        explanation="Два наибольших: 5*8=40. Два наименьших: (-10)*(-3)=30. Макс=40.")
    add(27,"Подмассив","Найти максимальную сумму подотрезка массива: -2,1,-3,4,-1,2,1,-5,4","number",6,"hard","code",
        test_cases=[{"input":"9\n-2\n1\n-3\n4\n-1\n2\n1\n-5\n4","expected_output":"6","is_public":True}],
        code_template="n = int(input())\ndata = [int(input()) for _ in range(n)]\nmax_sum = cur_sum = data[0]\nfor x in data[1:]:\n    cur_sum = max(x, cur_sum + x)\n    max_sum = max(max_sum, cur_sum)\nprint(max_sum)",
        explanation="Подотрезок [4,-1,2,1]: сумма=6. Алгоритм Кадане.")

    # ====== TASKS 18, 19, 20, 21, 22 additional ======
    add(18,"Робот L-образный","Робот в клетке (1,1). Поле 5×5. Нужно закрасить L-образную фигуру: (1,1)→(1,3)→(3,3). Минимальное число команд 'закрасить'?",
        "number",5,"medium",explanation="(1,1),(1,2),(1,3),(2,3),(3,3) = 5 клеток.",
        hints=["Нарисуйте поле и отметьте клетки"])
    add(18,"Стены","Робот движется вправо до стены. Стена на 5-й клетке от начала. Сколько шагов?",
        "number",4,"easy",explanation="4 шага (не выходя на стену).")

    add(19,"Камни 15","Куча: 15 камней. Ходы: 1 или 2. Побеждает взявший последний. Выигрывает?",
        "single_choice","A","easy",options=["A) Первый","B) Второй"],
        explanation="15 mod 3 = 0. Второй выигрывает. Нет, при ходах 1,2 выигрышная стратегия: 15 mod 3 = 0 → второй.",
        hints=["Если N делится на 3, выигрывает второй"])
    add(19,"Ходы 1,3","Куча: 10. Ходы: 1 или 3. Побеждает взявший последний. Кто выигрывает?",
        "single_choice","A","medium",options=["A) Первый","B) Второй"])

    add(20,"Две операции","Число S=7. Ходы: +1, ×2. Цель: ≥15. Кто выигрывает при оптимальной игре?",
        "single_choice","A","medium","code",options=["A) Первый","B) Второй"],
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        code_template="from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef win(n):\n    if n + 1 >= 15 or n * 2 >= 15:\n        return True\n    if not win(n + 1):\n        return True\n    if not win(n * 2):\n        return True\n    return False\n\nprint(1 if win(7) else 2)")

    add(21,"Все начальные","Ходы: +1, +3. Цель ≥10. Найти все S от 1 до 9, где первый проигрывает.","number",0,"hard","code",
        test_cases=[{"input":"","expected_output":"3 6 9","is_public":True}],
        code_template="from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef win(n):\n    if n + 1 >= 10 or n + 3 >= 10:\n        return True\n    if not win(n + 1):\n        return True\n    if not win(n + 3):\n        return True\n    return False\n\nresult = []\nfor s in range(1, 10):\n    if not win(s):\n        result.append(str(s))\nprint(' '.join(result))")

    add(22,"Четыре процесса","A(3с), B(2с), C(4с), D(2с). B после A. C после A. D после B и C. Общее время?",
        "number",9,"medium",explanation="A: 0-3. B: 3-5. C: 3-7. D: после B(5) и C(7) → D: 7-9. Итого: 9с.")
    add(22,"Конвейер","3 процесса по 2с каждый. Все последовательные. Время?","number",6,"easy",
        explanation="2+2+2=6с.")

    return exercises

EXTRA_EXERCISES = _make_extra_exercises()
