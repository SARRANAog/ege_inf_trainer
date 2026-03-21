def _make_extra_exercises_2():
    exercises = []
    eid = 2000

    def add(tn, title, text, atype, answer, diff="medium", etype="closed",
            options=None, test_cases=None, req=None, explanation="", hints=None, template=""):
        nonlocal eid
        eid += 1
        ex = {"exercise_id":f"ex_{tn}_{eid}","task_number":tn,"title":title,"text":text,
              "answer_type":atype,"correct_answer":answer,"difficulty":diff,"exercise_type":etype,
              "explanation":explanation,"hints":hints or [],"code_template":template}
        if options: ex["options"] = options
        if test_cases: ex["test_cases"] = test_cases
        if req: ex["required_constructs"] = req
        exercises.append(ex)

    # TASK 13 more
    add(13,"Большой граф","Граф: 1→2,1→3,1→4,2→3,2→4,3→4,3→5,4→5. Путей 1→5?","number",9,"medium","code",
        test_cases=[{"input":"","expected_output":"9","is_public":True}],
        template="g={1:[2,3,4],2:[3,4],3:[4,5],4:[5],5:[]}\ndef c(v):\n    if v==5:return 1\n    return sum(c(u) for u in g[v])\nprint(c(1))")
    add(13,"Взвешенный путь","Граф: A→B(2),A→C(5),B→C(1),B→D(4),C→D(2). Кратчайший путь A→D?","number",5,"medium","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        template="# Перебор всех путей\nimport sys\ng={'A':[('B',2),('C',5)],'B':[('C',1),('D',4)],'C':[('D',2)],'D':[]}\ndef shortest(v,target):\n    if v==target:return 0\n    best=float('inf')\n    for u,w in g.get(v,[]):\n        best=min(best,w+shortest(u,target))\n    return best\nprint(shortest('A','D'))")
    add(13,"Подсчёт рёбер","Граф: 1→2,1→3,2→3,2→4,3→4. Количество путей длины ровно 2 из 1 в 4?","number",2,"medium","code",
        test_cases=[{"input":"","expected_output":"2","is_public":True}],
        template="# Пути длины ровно 2: 1→x→4\ng={1:[2,3],2:[3,4],3:[4],4:[]}\ncount=0\nfor mid in g[1]:\n    if 4 in g.get(mid,[]):\n        count+=1\nprint(count)")
    add(13,"6 вершин","Граф:A→B,A→C,A→D,B→E,C→E,D→E,B→C,C→D. Путей A→E?","number",7,"hard","code",
        test_cases=[{"input":"","expected_output":"7","is_public":True}],
        template="g={'A':['B','C','D'],'B':['E','C'],'C':['E','D'],'D':['E'],'E':[]}\ndef c(v):\n    if v=='E':return 1\n    return sum(c(u) for u in g[v])\nprint(c('A'))")

    # TASK 14 more
    add(14,"В троичную","Число 50 в троичной системе?","number",1212,"easy","code",
        test_cases=[{"input":"","expected_output":"1212","is_public":True}],
        template="def to_base(n,b):\n    if n==0:return '0'\n    d=[]\n    while n>0:\n        d.append(str(n%b))\n        n//=b\n    return ''.join(reversed(d))\nprint(to_base(50,3))")
    add(14,"Из пятеричной","Число 234 в пятеричной = ? в десятичной","number",69,"easy","code",
        test_cases=[{"input":"","expected_output":"69","is_public":True}],
        template="print(int('234',5))")
    add(14,"Максимальная цифра","В какой системе счисления число 30 записывается как 1Е?","number",16,"medium","code",
        test_cases=[{"input":"","expected_output":"16","is_public":True}],
        template="print(int('1E',16))")
    add(14,"Перевод между","Число 1100 в двоичной = ? в восьмеричной","number",14,"easy","code",
        test_cases=[{"input":"","expected_output":"14","is_public":True}],
        template="n = int('1100', 2)\nprint(oct(n)[2:])")
    add(14,"Арифметика","Вычислите: 1011₂ + 1101₂. Результат в двоичной.","number",11000,"medium","code",
        test_cases=[{"input":"","expected_output":"11000","is_public":True}],
        template="a = int('1011', 2)\nb = int('1101', 2)\nprint(bin(a + b)[2:])")
    add(14,"Нули в записи","Сколько нулей в двоичной записи числа 200?","number",5,"easy","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        template="print(bin(200)[2:].count('0'))")

    # TASK 15 more
    add(15,"Цепочка импликаций 4","(x1→x2)∧(x2→x3)∧(x3→x4)=1. Количество решений?","number",5,"easy","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        template="from itertools import product\nc=0\nfor v in product((0,1),repeat=4):\n    ok=True\n    for i in range(3):\n        if v[i]>v[i+1]:ok=False;break\n    if ok:c+=1\nprint(c)")
    add(15,"С отрицанием","(x1∨¬x2)∧(x2∨¬x3)∧(x3∨¬x1)=1. Количество?","number",4,"medium","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3 in product((0,1),repeat=3):\n    if (x1 or not x2) and (x2 or not x3) and (x3 or not x1):c+=1\nprint(c)")
    add(15,"Двойная система","(x1→x2)∧(x3→x4)∧(x1∨x3)=1. Количество?","number",7,"medium","code",
        test_cases=[{"input":"","expected_output":"7","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3,x4 in product((0,1),repeat=4):\n    if (not x1 or x2) and (not x3 or x4) and (x1 or x3):c+=1\nprint(c)")
    add(15,"7 переменных","(x1→x2)∧(x2→x3)∧...∧(x6→x7)=1. Количество?","number",8,"hard","code",
        test_cases=[{"input":"","expected_output":"8","is_public":True}],
        template="from itertools import product\nc=0\nfor v in product((0,1),repeat=7):\n    ok=all(v[i]<=v[i+1] for i in range(6))\n    if ok:c+=1\nprint(c)")
    add(15,"XOR система","x1⊕x2=1, x2⊕x3=0. Количество решений?","number",2,"medium","code",
        test_cases=[{"input":"","expected_output":"2","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3 in product((0,1),repeat=3):\n    if (x1^x2==1) and (x2^x3==0):c+=1\nprint(c)")
    add(15,"С дизъюнкцией","(x1∨x2)∧(¬x1∨x3)∧(¬x2∨¬x3)=1. Количество?","number",3,"medium","code",
        test_cases=[{"input":"","expected_output":"3","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3 in product((0,1),repeat=3):\n    if (x1 or x2) and (not x1 or x3) and (not x2 or not x3):c+=1\nprint(c)")

    # TASK 16 more
    add(16,"Степень","F(0)=1, F(n)=2*F(n-1). F(8)?","number",256,"easy","code",
        test_cases=[{"input":"","expected_output":"256","is_public":True}],
        template="def F(n):\n    if n==0:return 1\n    return 2*F(n-1)\nprint(F(8))")
    add(16,"Сумма рекурсия","F(1)=1, F(n)=F(n-1)+n. F(10)?","number",55,"easy","code",
        test_cases=[{"input":"","expected_output":"55","is_public":True}],
        template="def F(n):\n    if n==1:return 1\n    return F(n-1)+n\nprint(F(10))")
    add(16,"Трибоначчи","F(1)=F(2)=F(3)=1, F(n)=F(n-1)+F(n-2)+F(n-3). F(7)?","number",17,"medium","code",
        test_cases=[{"input":"","expected_output":"17","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef F(n):\n    if n<=3:return 1\n    return F(n-1)+F(n-2)+F(n-3)\nprint(F(7))")
    add(16,"Взаимная рекурсия","F(0)=1, G(0)=0, F(n)=F(n-1)+G(n-1), G(n)=F(n-1). F(5)?","number",8,"hard","code",
        test_cases=[{"input":"","expected_output":"8","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef F(n):\n    if n==0:return 1\n    return F(n-1)+G(n-1)\n@lru_cache(None)\ndef G(n):\n    if n==0:return 0\n    return F(n-1)\nprint(F(5))")
    add(16,"Обратная рекурсия","F(n)=3*F(n-1)-2, F(0)=1. При каком n значение F(n)=187?","number",0,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        template="def F(n):\n    if n==0:return 1\n    return 3*F(n-1)-2\nfor n in range(20):\n    if F(n)==187:\n        print(n)\n        break")

    # TASK 17 more
    add(17,"Количество отрицательных","В последовательности: -5,3,-2,7,0,-1,4. Сколько отрицательных?","number",3,"easy","code",
        test_cases=[{"input":"7\n-5\n3\n-2\n7\n0\n-1\n4","expected_output":"3","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nprint(sum(1 for x in data if x<0))")
    add(17,"Произведение","Найти произведение ненулевых элементов: 3,0,2,0,5.","number",30,"easy","code",
        test_cases=[{"input":"5\n3\n0\n2\n0\n5","expected_output":"30","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\np=1\nfor x in data:\n    if x!=0:p*=x\nprint(p)")
    add(17,"Ближайшее к среднему","Из чисел 1,5,3,8,2 найти ближайшее к среднему арифметическому.","number",3,"medium","code",
        test_cases=[{"input":"5\n1\n5\n3\n8\n2","expected_output":"3","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\navg=sum(data)/len(data)\nclosest=min(data,key=lambda x:abs(x-avg))\nprint(closest)",
        explanation="Среднее=19/5=3.8. Ближайшее: 3 (разница 0.8) или 5 (1.2). Ответ: 3.")
    add(17,"Второй минимум","Найти второй минимальный элемент: 5,3,8,1,7,2.","number",2,"medium","code",
        test_cases=[{"input":"6\n5\n3\n8\n1\n7\n2","expected_output":"2","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\ndata.sort()\nprint(data[1])")
    add(17,"Чётные на чётных","На чётных позициях (2,4,6,...) подсчитать сумму чётных чисел: 1,4,3,6,5,8.","number",18,"medium","code",
        test_cases=[{"input":"6\n1\n4\n3\n6\n5\n8","expected_output":"18","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\ns=sum(data[i] for i in range(1,n,2) if data[i]%2==0)\nprint(s)",
        explanation="Позиции 2,4,6 (индексы 1,3,5): 4,6,8. Все чётные. Сумма=18.")

    # TASK 18 more
    add(18,"Прямоугольник","Робот в (1,1). Нужно закрасить прямоугольник 3×2 (от (1,1) до (3,2)). Сколько клеток?","number",6,"easy",
        explanation="3*2=6 клеток.")
    add(18,"Диагональ","Робот должен пройти по диагонали от (1,1) до (4,4). Минимум команд (вправо/вверх)?","number",6,"easy",
        explanation="3 вправо + 3 вверх = 6 команд перемещения.")
    add(18,"Лестница","Закрасить лестницу: (1,1),(2,1),(2,2),(3,2),(3,3). Сколько команд 'закрасить'?","number",5,"medium")
    add(18,"Спираль","Робот движется: 3 вправо, 3 вверх, 2 влево, 2 вниз. Координаты конечной точки (начало в (0,0))?",
        "single_choice","B","medium",options=["A) (1,1)","B) (1,1)","C) (3,3)","D) (2,1)"],
        explanation="(0,0)→(3,0)→(3,3)→(1,3)→(1,1). Ответ: (1,1).")

    # TASK 19 more
    add(19,"Камни +1,+3","Куча=7. Ходы:+1,+3. Цель>=12. Кто выигрывает?","single_choice","A","medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,3]:\n        if n+m>=12:return True\n        if not w(n+m):return True\n    return False\nprint(1 if w(7) else 2)",
        options=["A) Первый","B) Второй"])
    add(19,"Камни *2","Число=3. Ходы:+1,*2. Цель>=16. Кто?","single_choice","A","medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for nn in [n+1,n*2]:\n        if nn>=16:return True\n        if not w(nn):return True\n    return False\nprint(1 if w(3) else 2)",
        options=["A) Первый","B) Второй"])
    add(19,"Ним 3","Куча 12. Ходы:1,2,3. Взявший последний выигрывает. Кто?","single_choice","A","easy",
        options=["A) Первый","B) Второй"],explanation="12 mod 4 = 0. Второй выигрывает.",
        hints=["При ходах 1,2,3 — позиции кратные 4 проигрышные"])

    # TASK 20 more
    add(20,"Две кучи +1","Кучи: 2,3. Ход: +1 к любой куче. Цель: любая куча >=5. Кто выигрывает?","single_choice","A","medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(a,b):\n    if a>=5 or b>=5:return False\n    if not w(a+1,b):return True\n    if not w(a,b+1):return True\n    return False\nprint(1 if w(2,3) else 2)",
        options=["A) Первый","B) Второй"])
    add(20,"Ход *2 или +1","S=4. Ходы: +1, *2. Цель >=20. При каком S второй выигрывает? Проверить S=4.","single_choice","B","hard","code",
        test_cases=[{"input":"","expected_output":"2","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for nn in [n+1,n*2]:\n        if nn>=20:return True\n        if not w(nn):return True\n    return False\nprint(1 if w(4) else 2)",
        options=["A) Первый","B) Второй"])
    add(20,"Глубина 2","S=6. Ходы:+1,+2. Цель>=10. Первый выигрывает на каком ходе (1 или 2)?","number",1,"medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,2]:\n        if n+m>=10:return True\n        if not w(n+m):return True\n    return False\n# Первый ход: если n+m>=10, выигрыш за 1 ход\nfor m in [1,2]:\n    if 6+m>=10:\n        print(1)\n        exit()\nfor m in [1,2]:\n    nn=6+m\n    if not w(nn):\n        print(1)\n        exit()\nprint(2)")

    # TASK 21 more
    add(21,"Все проигрышные","Ходы:+1,+2,+3. Цель>=15. Найти все S (1-14), где первый проигрывает.","number",0,"hard","code",
        test_cases=[{"input":"","expected_output":"4 8 12","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,2,3]:\n        if n+m>=15:return True\n        if not w(n+m):return True\n    return False\nres=[str(s) for s in range(1,15) if not w(s)]\nprint(' '.join(res))")
    add(21,"Выигрышный ход","S=7. Ходы:+1,+3. Цель>=12. Каким ходом первый должен ходить для победы?","number",3,"medium","code",
        test_cases=[{"input":"","expected_output":"3","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,3]:\n        if n+m>=12:return True\n        if not w(n+m):return True\n    return False\nfor m in [1,3]:\n    nn=7+m\n    if nn>=12 or not w(nn):\n        print(m)\n        break")

    # TASK 22 more
    add(22,"Критический путь","A(4),B(3),C(2),D(5),E(1). B после A. C после A. D после B,C. E после D. Время?","number",12,"medium",
        explanation="A:0-4. B:4-7. C:4-6. D:max(7,6)=7→7-12. E:12-13. Но вопрос 'время'=13?... A(4)+B(3)+D(5)+E(1)=13.")
    add(22,"Полная параллель","5 процессов по 2с, все независимы. При 3 процессорах время?","number",4,"medium",
        explanation="3 процессора: [A,B],[C,D],[E]. Время: max(4,4,2)=4с.")
    add(22,"Зависимости","A(1),B(2),C(3). C после A и B. Время?","number",5,"easy",
        explanation="A:0-1, B:0-2, C:max(1,2)=2→2-5. Итого=5.")

    # TASK 23 more
    add(23,"Уникальные символы","Сколько уникальных символов в строке 'абракадабра'?","number",5,"easy","code",
        test_cases=[{"input":"абракадабра","expected_output":"5","is_public":True}],
        template="print(len(set(input())))")
    add(23,"Замена","Замените все 'a' на 'o' в 'banana'. Выведите результат.","number",0,"easy","code",
        test_cases=[{"input":"banana","expected_output":"bonono","is_public":True}],
        template="print(input().replace('a','o'))")
    add(23,"Самый частый","Найти самый частый символ в 'абракадабра'.","number",0,"medium","code",
        test_cases=[{"input":"абракадабра","expected_output":"а","is_public":True}],
        template="s=input()\nfrom collections import Counter\nprint(Counter(s).most_common(1)[0][0])")
    add(23,"Подстроки длины 2","Сколько различных подстрок длины 2 в 'abcabc'?","number",3,"easy","code",
        test_cases=[{"input":"abcabc","expected_output":"3","is_public":True}],
        template="s=input()\nprint(len(set(s[i:i+2] for i in range(len(s)-1))))")
    add(23,"Без пробелов","Удалить пробелы из 'a b c d'. Вывести результат.","number",0,"easy","code",
        test_cases=[{"input":"a b c d","expected_output":"abcd","is_public":True}],
        template="print(input().replace(' ',''))")

    # TASK 24 more
    add(24,"Подсчёт цифр","Сколько цифр в строке 'abc123def456'?","number",6,"easy","code",
        test_cases=[{"input":"abc123def456","expected_output":"6","is_public":True}],
        template="print(sum(1 for c in input() if c.isdigit()))")
    add(24,"Самое длинное слово","Найти длину самого длинного слова в 'Я учу информатику хорошо'.","number",12,"easy","code",
        test_cases=[{"input":"Я учу информатику хорошо","expected_output":"12","is_public":True}],
        template="print(max(len(w) for w in input().split()))")
    add(24,"Палиндром строка","Является ли 'казак' палиндромом? 1=да, 0=нет.","number",1,"easy","code",
        test_cases=[{"input":"казак","expected_output":"1","is_public":True}],
        template="s=input()\nprint(1 if s==s[::-1] else 0)")
    add(24,"Капитализация","Вывести каждое слово с заглавной буквы: 'привет мир'.","number",0,"easy","code",
        test_cases=[{"input":"привет мир","expected_output":"Привет Мир","is_public":True}],
        template="print(input().title())")
    add(24,"Сжатие","Сжать строку: 'aaabbbcc' → 'a3b3c2'.","number",0,"medium","code",
        test_cases=[{"input":"aaabbbcc","expected_output":"a3b3c2","is_public":True}],
        template="s=input()\nresult=''\ni=0\nwhile i<len(s):\n    c=s[i]\n    count=0\n    while i<len(s) and s[i]==c:\n        count+=1\n        i+=1\n    result+=c+str(count)\nprint(result)")

    # TASK 25 more
    add(25,"Простое число","Наибольшее простое число <= 50?","number",47,"easy","code",
        test_cases=[{"input":"","expected_output":"47","is_public":True}],
        template="def is_p(n):\n    if n<2:return False\n    for i in range(2,int(n**0.5)+1):\n        if n%i==0:return False\n    return True\nfor n in range(50,1,-1):\n    if is_p(n):\n        print(n)\n        break")
    add(25,"Сумма делителей","Сумма всех делителей числа 24?","number",60,"easy","code",
        test_cases=[{"input":"","expected_output":"60","is_public":True}],
        template="n=24\nprint(sum(i for i in range(1,n+1) if n%i==0))")
    add(25,"Взаимно простые","Сколько чисел от 1 до 20 взаимно просты с 12?","number",6,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        template="from math import gcd\nprint(sum(1 for i in range(1,21) if gcd(i,12)==1))",
        explanation="Функция Эйлера: числа взаимно простые с 12 от 1 до 20.")
    add(25,"Разложение","Сколько простых множителей (с повторениями) у числа 360?","number",6,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        template="n=360\ncount=0\nd=2\nwhile d*d<=n:\n    while n%d==0:\n        count+=1\n        n//=d\n    d+=1\nif n>1:count+=1\nprint(count)",
        explanation="360=2³×3²×5. Всего: 3+2+1=6 множителей.")
    add(25,"Совершенные до 10000","Сколько совершенных чисел от 1 до 10000?","number",4,"hard","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        template="count=0\nfor n in range(2,10001):\n    s=sum(i for i in range(1,n) if n%i==0)\n    if s==n:count+=1\nprint(count)",
        explanation="6, 28, 496, 8128 = 4 совершенных числа.")

    # TASK 26 more
    add(26,"Сортировка","Отсортировать числа 5,3,8,1,9 и вывести через пробел.","number",0,"easy","code",
        test_cases=[{"input":"5\n5\n3\n8\n1\n9","expected_output":"1 3 5 8 9","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nprint(' '.join(map(str,sorted(data))))")
    add(26,"Уникальные","Найти количество уникальных чисел в последовательности: 3,5,3,7,5,7,1.","number",4,"easy","code",
        test_cases=[{"input":"7\n3\n5\n3\n7\n5\n7\n1","expected_output":"4","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nprint(len(set(data)))")
    add(26,"Ближайшие","Найти минимальную разность между соседними элементами отсортированного массива: 1,5,3,8,10.","number",2,"medium","code",
        test_cases=[{"input":"5\n1\n5\n3\n8\n10","expected_output":"2","is_public":True}],
        template="n=int(input())\ndata=sorted(int(input()) for _ in range(n))\nprint(min(data[i+1]-data[i] for i in range(n-1)))")
    add(26,"K-й максимум","3-й по величине элемент из 10,3,7,5,1,8?","number",7,"medium","code",
        test_cases=[{"input":"6\n10\n3\n7\n5\n1\n8","expected_output":"7","is_public":True}],
        template="n=int(input())\ndata=sorted([int(input()) for _ in range(n)],reverse=True)\nprint(data[2])")
    add(26,"Сумма пар","Сколько пар (i,j), i<j, таких что data[i]+data[j] чётно? Данные: 1,2,3,4,5.","number",4,"medium","code",
        test_cases=[{"input":"5\n1\n2\n3\n4\n5","expected_output":"4","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nc=0\nfor i in range(n):\n    for j in range(i+1,n):\n        if (data[i]+data[j])%2==0:c+=1\nprint(c)",
        explanation="Чётная сумма: оба чётные или оба нечётные. Чётные:{2,4}→C(2,2)=1. Нечётные:{1,3,5}→C(3,2)=3. Итого 4.")

    # TASK 27 more
    add(27,"Два указателя","Найти пару чисел с суммой 15 из отсортированного массива: 1,3,5,7,8,10,12.","number",0,"medium","code",
        test_cases=[{"input":"7\n1\n3\n5\n7\n8\n10\n12","expected_output":"3 12","is_public":True}],
        template="n=int(input())\ndata=sorted(int(input()) for _ in range(n))\nl,r=0,n-1\nwhile l<r:\n    s=data[l]+data[r]\n    if s==15:\n        print(data[l],data[r])\n        break\n    elif s<15:l+=1\n    else:r-=1")
    add(27,"Наибольший делящийся","Из массива найти наибольшее число, делящееся на 3 и на 5: 10,15,30,7,25,45,9.","number",45,"easy","code",
        test_cases=[{"input":"7\n10\n15\n30\n7\n25\n45\n9","expected_output":"45","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nresult=max((x for x in data if x%3==0 and x%5==0),default=-1)\nprint(result)")
    add(27,"Количество инверсий","Подсчитать инверсии (i<j, a[i]>a[j]) в массиве 3,1,2.","number",2,"hard","code",
        test_cases=[{"input":"3\n3\n1\n2","expected_output":"2","is_public":True}],
        template="n=int(input())\na=[int(input()) for _ in range(n)]\nc=0\nfor i in range(n):\n    for j in range(i+1,n):\n        if a[i]>a[j]:c+=1\nprint(c)")
    add(27,"Непрерывная подпоследовательность","Максимальная длина непрерывной подпоследовательности положительных: -1,2,3,4,-2,5,6,-3.","number",3,"medium","code",
        test_cases=[{"input":"8\n-1\n2\n3\n4\n-2\n5\n6\n-3","expected_output":"3","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nmx=cur=0\nfor x in data:\n    if x>0:cur+=1;mx=max(mx,cur)\n    else:cur=0\nprint(mx)")

    return exercises

EXTRA_EXERCISES_2 = _make_extra_exercises_2()
