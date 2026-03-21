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
    add(13,"\u0411\u043e\u043b\u044c\u0448\u043e\u0439 \u0433\u0440\u0430\u0444","\u0413\u0440\u0430\u0444: 1\u21922,1\u21923,1\u21924,2\u21923,2\u21924,3\u21924,3\u21925,4\u21925. \u041f\u0443\u0442\u0435\u0439 1\u21925?","number",9,"medium","code",
        test_cases=[{"input":"","expected_output":"9","is_public":True}],
        template="g={1:[2,3,4],2:[3,4],3:[4,5],4:[5],5:[]}\ndef c(v):\n    if v==5:return 1\n    return sum(c(u) for u in g[v])\nprint(c(1))")
    add(13,"\u0412\u0437\u0432\u0435\u0448\u0435\u043d\u043d\u044b\u0439 \u043f\u0443\u0442\u044c","\u0413\u0440\u0430\u0444: A\u2192B(2),A\u2192C(5),B\u2192C(1),B\u2192D(4),C\u2192D(2). \u041a\u0440\u0430\u0442\u0447\u0430\u0439\u0448\u0438\u0439 \u043f\u0443\u0442\u044c A\u2192D?","number",5,"medium","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        template="# \u041f\u0435\u0440\u0435\u0431\u043e\u0440 \u0432\u0441\u0435\u0445 \u043f\u0443\u0442\u0435\u0439\nimport sys\ng={'A':[('B',2),('C',5)],'B':[('C',1),('D',4)],'C':[('D',2)],'D':[]}\ndef shortest(v,target):\n    if v==target:return 0\n    best=float('inf')\n    for u,w in g.get(v,[]):\n        best=min(best,w+shortest(u,target))\n    return best\nprint(shortest('A','D'))")
    add(13,"\u041f\u043e\u0434\u0441\u0447\u0451\u0442 \u0440\u0451\u0431\u0435\u0440","\u0413\u0440\u0430\u0444: 1\u21922,1\u21923,2\u21923,2\u21924,3\u21924. \u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u0443\u0442\u0435\u0439 \u0434\u043b\u0438\u043d\u044b \u0440\u043e\u0432\u043d\u043e 2 \u0438\u0437 1 \u0432 4?","number",2,"medium","code",
        test_cases=[{"input":"","expected_output":"2","is_public":True}],
        template="# \u041f\u0443\u0442\u0438 \u0434\u043b\u0438\u043d\u044b \u0440\u043e\u0432\u043d\u043e 2: 1\u2192x\u21924\ng={1:[2,3],2:[3,4],3:[4],4:[]}\ncount=0\nfor mid in g[1]:\n    if 4 in g.get(mid,[]):\n        count+=1\nprint(count)")
    add(13,"6 \u0432\u0435\u0440\u0448\u0438\u043d","\u0413\u0440\u0430\u0444:A\u2192B,A\u2192C,A\u2192D,B\u2192E,C\u2192E,D\u2192E,B\u2192C,C\u2192D. \u041f\u0443\u0442\u0435\u0439 A\u2192E?","number",7,"hard","code",
        test_cases=[{"input":"","expected_output":"7","is_public":True}],
        template="g={'A':['B','C','D'],'B':['E','C'],'C':['E','D'],'D':['E'],'E':[]}\ndef c(v):\n    if v=='E':return 1\n    return sum(c(u) for u in g[v])\nprint(c('A'))")

    # TASK 14 more
    add(14,"\u0412 \u0442\u0440\u043e\u0438\u0447\u043d\u0443\u044e","\u0427\u0438\u0441\u043b\u043e 50 \u0432 \u0442\u0440\u043e\u0438\u0447\u043d\u043e\u0439 \u0441\u0438\u0441\u0442\u0435\u043c\u0435?","number",1212,"easy","code",
        test_cases=[{"input":"","expected_output":"1212","is_public":True}],
        template="def to_base(n,b):\n    if n==0:return '0'\n    d=[]\n    while n>0:\n        d.append(str(n%b))\n        n//=b\n    return ''.join(reversed(d))\nprint(to_base(50,3))")
    add(14,"\u0418\u0437 \u043f\u044f\u0442\u0435\u0440\u0438\u0447\u043d\u043e\u0439","\u0427\u0438\u0441\u043b\u043e 234 \u0432 \u043f\u044f\u0442\u0435\u0440\u0438\u0447\u043d\u043e\u0439 = ? \u0432 \u0434\u0435\u0441\u044f\u0442\u0438\u0447\u043d\u043e\u0439","number",69,"easy","code",
        test_cases=[{"input":"","expected_output":"69","is_public":True}],
        template="print(int('234',5))")
    add(14,"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0446\u0438\u0444\u0440\u0430","\u0412 \u043a\u0430\u043a\u043e\u0439 \u0441\u0438\u0441\u0442\u0435\u043c\u0435 \u0441\u0447\u0438\u0441\u043b\u0435\u043d\u0438\u044f \u0447\u0438\u0441\u043b\u043e 30 \u0437\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u043a\u0430\u043a 1\u0415?","number",16,"medium","code",
        test_cases=[{"input":"","expected_output":"16","is_public":True}],
        template="print(int('1E',16))")
    add(14,"\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u043c\u0435\u0436\u0434\u0443","\u0427\u0438\u0441\u043b\u043e 1100 \u0432 \u0434\u0432\u043e\u0438\u0447\u043d\u043e\u0439 = ? \u0432 \u0432\u043e\u0441\u044c\u043c\u0435\u0440\u0438\u0447\u043d\u043e\u0439","number",14,"easy","code",
        test_cases=[{"input":"","expected_output":"14","is_public":True}],
        template="n = int('1100', 2)\nprint(oct(n)[2:])")
    add(14,"\u0410\u0440\u0438\u0444\u043c\u0435\u0442\u0438\u043a\u0430","\u0412\u044b\u0447\u0438\u0441\u043b\u0438\u0442\u0435: 1011\u2082 + 1101\u2082. \u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u0432 \u0434\u0432\u043e\u0438\u0447\u043d\u043e\u0439.","number",11000,"medium","code",
        test_cases=[{"input":"","expected_output":"11000","is_public":True}],
        template="a = int('1011', 2)\nb = int('1101', 2)\nprint(bin(a + b)[2:])")
    add(14,"\u041d\u0443\u043b\u0438 \u0432 \u0437\u0430\u043f\u0438\u0441\u0438","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043d\u0443\u043b\u0435\u0439 \u0432 \u0434\u0432\u043e\u0438\u0447\u043d\u043e\u0439 \u0437\u0430\u043f\u0438\u0441\u0438 \u0447\u0438\u0441\u043b\u0430 200?","number",5,"easy","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        template="print(bin(200)[2:].count('0'))")

    # TASK 15 more
    add(15,"\u0426\u0435\u043f\u043e\u0447\u043a\u0430 \u0438\u043c\u043f\u043b\u0438\u043a\u0430\u0446\u0438\u0439 4","(x1\u2192x2)\u2227(x2\u2192x3)\u2227(x3\u2192x4)=1. \u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0440\u0435\u0448\u0435\u043d\u0438\u0439?","number",5,"easy","code",
        test_cases=[{"input":"","expected_output":"5","is_public":True}],
        template="from itertools import product\nc=0\nfor v in product((0,1),repeat=4):\n    ok=True\n    for i in range(3):\n        if v[i]>v[i+1]:ok=False;break\n    if ok:c+=1\nprint(c)")
    add(15,"\u0421 \u043e\u0442\u0440\u0438\u0446\u0430\u043d\u0438\u0435\u043c","(x1\u2228\xacx2)\u2227(x2\u2228\xacx3)\u2227(x3\u2228\xacx1)=1. \u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e?","number",4,"medium","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3 in product((0,1),repeat=3):\n    if (x1 or not x2) and (x2 or not x3) and (x3 or not x1):c+=1\nprint(c)")
    add(15,"\u0414\u0432\u043e\u0439\u043d\u0430\u044f \u0441\u0438\u0441\u0442\u0435\u043c\u0430","(x1\u2192x2)\u2227(x3\u2192x4)\u2227(x1\u2228x3)=1. \u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e?","number",7,"medium","code",
        test_cases=[{"input":"","expected_output":"7","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3,x4 in product((0,1),repeat=4):\n    if (not x1 or x2) and (not x3 or x4) and (x1 or x3):c+=1\nprint(c)")
    add(15,"7 \u043f\u0435\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0445","(x1\u2192x2)\u2227(x2\u2192x3)\u2227...\u2227(x6\u2192x7)=1. \u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e?","number",8,"hard","code",
        test_cases=[{"input":"","expected_output":"8","is_public":True}],
        template="from itertools import product\nc=0\nfor v in product((0,1),repeat=7):\n    ok=all(v[i]<=v[i+1] for i in range(6))\n    if ok:c+=1\nprint(c)")
    add(15,"XOR \u0441\u0438\u0441\u0442\u0435\u043c\u0430","x1\u2295x2=1, x2\u2295x3=0. \u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0440\u0435\u0448\u0435\u043d\u0438\u0439?","number",2,"medium","code",
        test_cases=[{"input":"","expected_output":"2","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3 in product((0,1),repeat=3):\n    if (x1^x2==1) and (x2^x3==0):c+=1\nprint(c)")
    add(15,"\u0421 \u0434\u0438\u0437\u044a\u044e\u043d\u043a\u0446\u0438\u0435\u0439","(x1\u2228x2)\u2227(\xacx1\u2228x3)\u2227(\xacx2\u2228\xacx3)=1. \u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e?","number",3,"medium","code",
        test_cases=[{"input":"","expected_output":"3","is_public":True}],
        template="from itertools import product\nc=0\nfor x1,x2,x3 in product((0,1),repeat=3):\n    if (x1 or x2) and (not x1 or x3) and (not x2 or not x3):c+=1\nprint(c)")

    # TASK 16 more
    add(16,"\u0421\u0442\u0435\u043f\u0435\u043d\u044c","F(0)=1, F(n)=2*F(n-1). F(8)?","number",256,"easy","code",
        test_cases=[{"input":"","expected_output":"256","is_public":True}],
        template="def F(n):\n    if n==0:return 1\n    return 2*F(n-1)\nprint(F(8))")
    add(16,"\u0421\u0443\u043c\u043c\u0430 \u0440\u0435\u043a\u0443\u0440\u0441\u0438\u044f","F(1)=1, F(n)=F(n-1)+n. F(10)?","number",55,"easy","code",
        test_cases=[{"input":"","expected_output":"55","is_public":True}],
        template="def F(n):\n    if n==1:return 1\n    return F(n-1)+n\nprint(F(10))")
    add(16,"\u0422\u0440\u0438\u0431\u043e\u043d\u0430\u0447\u0447\u0438","F(1)=F(2)=F(3)=1, F(n)=F(n-1)+F(n-2)+F(n-3). F(7)?","number",17,"medium","code",
        test_cases=[{"input":"","expected_output":"17","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef F(n):\n    if n<=3:return 1\n    return F(n-1)+F(n-2)+F(n-3)\nprint(F(7))")
    add(16,"\u0412\u0437\u0430\u0438\u043c\u043d\u0430\u044f \u0440\u0435\u043a\u0443\u0440\u0441\u0438\u044f","F(0)=1, G(0)=0, F(n)=F(n-1)+G(n-1), G(n)=F(n-1). F(5)?","number",8,"hard","code",
        test_cases=[{"input":"","expected_output":"8","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef F(n):\n    if n==0:return 1\n    return F(n-1)+G(n-1)\n@lru_cache(None)\ndef G(n):\n    if n==0:return 0\n    return F(n-1)\nprint(F(5))")
    add(16,"\u041e\u0431\u0440\u0430\u0442\u043d\u0430\u044f \u0440\u0435\u043a\u0443\u0440\u0441\u0438\u044f","F(n)=3*F(n-1)-2, F(0)=1. \u041f\u0440\u0438 \u043a\u0430\u043a\u043e\u043c n \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 F(n)=187?","number",0,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        template="def F(n):\n    if n==0:return 1\n    return 3*F(n-1)-2\nfor n in range(20):\n    if F(n)==187:\n        print(n)\n        break")

    # TASK 17 more
    add(17,"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043e\u0442\u0440\u0438\u0446\u0430\u0442\u0435\u043b\u044c\u043d\u044b\u0445","\u0412 \u043f\u043e\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438: -5,3,-2,7,0,-1,4. \u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043e\u0442\u0440\u0438\u0446\u0430\u0442\u0435\u043b\u044c\u043d\u044b\u0445?","number",3,"easy","code",
        test_cases=[{"input":"7\n-5\n3\n-2\n7\n0\n-1\n4","expected_output":"3","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nprint(sum(1 for x in data if x<0))")
    add(17,"\u041f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0438\u0435","\u041d\u0430\u0439\u0442\u0438 \u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u043d\u0435\u043d\u0443\u043b\u0435\u0432\u044b\u0445 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u043e\u0432: 3,0,2,0,5.","number",30,"easy","code",
        test_cases=[{"input":"5\n3\n0\n2\n0\n5","expected_output":"30","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\np=1\nfor x in data:\n    if x!=0:p*=x\nprint(p)")
    add(17,"\u0411\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u043a \u0441\u0440\u0435\u0434\u043d\u0435\u043c\u0443","\u0418\u0437 \u0447\u0438\u0441\u0435\u043b 1,5,3,8,2 \u043d\u0430\u0439\u0442\u0438 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u043a \u0441\u0440\u0435\u0434\u043d\u0435\u043c\u0443 \u0430\u0440\u0438\u0444\u043c\u0435\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u043c\u0443.","number",3,"medium","code",
        test_cases=[{"input":"5\n1\n5\n3\n8\n2","expected_output":"3","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\navg=sum(data)/len(data)\nclosest=min(data,key=lambda x:abs(x-avg))\nprint(closest)",
        explanation="\u0421\u0440\u0435\u0434\u043d\u0435\u0435=19/5=3.8. \u0411\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435: 3 (\u0440\u0430\u0437\u043d\u0438\u0446\u0430 0.8) \u0438\u043b\u0438 5 (1.2). \u041e\u0442\u0432\u0435\u0442: 3.")
    add(17,"\u0412\u0442\u043e\u0440\u043e\u0439 \u043c\u0438\u043d\u0438\u043c\u0443\u043c","\u041d\u0430\u0439\u0442\u0438 \u0432\u0442\u043e\u0440\u043e\u0439 \u043c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 \u044d\u043b\u0435\u043c\u0435\u043d\u0442: 5,3,8,1,7,2.","number",2,"medium","code",
        test_cases=[{"input":"6\n5\n3\n8\n1\n7\n2","expected_output":"2","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\ndata.sort()\nprint(data[1])")
    add(17,"\u0427\u0451\u0442\u043d\u044b\u0435 \u043d\u0430 \u0447\u0451\u0442\u043d\u044b\u0445","\u041d\u0430 \u0447\u0451\u0442\u043d\u044b\u0445 \u043f\u043e\u0437\u0438\u0446\u0438\u044f\u0445 (2,4,6,...) \u043f\u043e\u0434\u0441\u0447\u0438\u0442\u0430\u0442\u044c \u0441\u0443\u043c\u043c\u0443 \u0447\u0451\u0442\u043d\u044b\u0445 \u0447\u0438\u0441\u0435\u043b: 1,4,3,6,5,8.","number",18,"medium","code",
        test_cases=[{"input":"6\n1\n4\n3\n6\n5\n8","expected_output":"18","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\ns=sum(data[i] for i in range(1,n,2) if data[i]%2==0)\nprint(s)",
        explanation="\u041f\u043e\u0437\u0438\u0446\u0438\u0438 2,4,6 (\u0438\u043d\u0434\u0435\u043a\u0441\u044b 1,3,5): 4,6,8. \u0412\u0441\u0435 \u0447\u0451\u0442\u043d\u044b\u0435. \u0421\u0443\u043c\u043c\u0430=18.")

    # TASK 18 more
    add(18,"\u041f\u0440\u044f\u043c\u043e\u0443\u0433\u043e\u043b\u044c\u043d\u0438\u043a","\u0420\u043e\u0431\u043e\u0442 \u0432 (1,1). \u041d\u0443\u0436\u043d\u043e \u0437\u0430\u043a\u0440\u0430\u0441\u0438\u0442\u044c \u043f\u0440\u044f\u043c\u043e\u0443\u0433\u043e\u043b\u044c\u043d\u0438\u043a 3\xd72 (\u043e\u0442 (1,1) \u0434\u043e (3,2)). \u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043a\u043b\u0435\u0442\u043e\u043a?","number",6,"easy",
        explanation="3*2=6 \u043a\u043b\u0435\u0442\u043e\u043a.")
    add(18,"\u0414\u0438\u0430\u0433\u043e\u043d\u0430\u043b\u044c","\u0420\u043e\u0431\u043e\u0442 \u0434\u043e\u043b\u0436\u0435\u043d \u043f\u0440\u043e\u0439\u0442\u0438 \u043f\u043e \u0434\u0438\u0430\u0433\u043e\u043d\u0430\u043b\u0438 \u043e\u0442 (1,1) \u0434\u043e (4,4). \u041c\u0438\u043d\u0438\u043c\u0443\u043c \u043a\u043e\u043c\u0430\u043d\u0434 (\u0432\u043f\u0440\u0430\u0432\u043e/\u0432\u0432\u0435\u0440\u0445)?","number",6,"easy",
        explanation="3 \u0432\u043f\u0440\u0430\u0432\u043e + 3 \u0432\u0432\u0435\u0440\u0445 = 6 \u043a\u043e\u043c\u0430\u043d\u0434 \u043f\u0435\u0440\u0435\u043c\u0435\u0449\u0435\u043d\u0438\u044f.")
    add(18,"\u041b\u0435\u0441\u0442\u043d\u0438\u0446\u0430","\u0417\u0430\u043a\u0440\u0430\u0441\u0438\u0442\u044c \u043b\u0435\u0441\u0442\u043d\u0438\u0446\u0443: (1,1),(2,1),(2,2),(3,2),(3,3). \u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043a\u043e\u043c\u0430\u043d\u0434 '\u0437\u0430\u043a\u0440\u0430\u0441\u0438\u0442\u044c'?","number",5,"medium")
    add(18,"\u0421\u043f\u0438\u0440\u0430\u043b\u044c","\u0420\u043e\u0431\u043e\u0442 \u0434\u0432\u0438\u0436\u0435\u0442\u0441\u044f: 3 \u0432\u043f\u0440\u0430\u0432\u043e, 3 \u0432\u0432\u0435\u0440\u0445, 2 \u0432\u043b\u0435\u0432\u043e, 2 \u0432\u043d\u0438\u0437. \u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b \u043a\u043e\u043d\u0435\u0447\u043d\u043e\u0439 \u0442\u043e\u0447\u043a\u0438 (\u043d\u0430\u0447\u0430\u043b\u043e \u0432 (0,0))?",
        "single_choice","B","medium",options=["A) (1,1)","B) (1,1)","C) (3,3)","D) (2,1)"],
        explanation="(0,0)\u2192(3,0)\u2192(3,3)\u2192(1,3)\u2192(1,1). \u041e\u0442\u0432\u0435\u0442: (1,1).")

    # TASK 19 more
    add(19,"\u041a\u0430\u043c\u043d\u0438 +1,+3","\u041a\u0443\u0447\u0430=7. \u0425\u043e\u0434\u044b:+1,+3. \u0426\u0435\u043b\u044c>=12. \u041a\u0442\u043e \u0432\u044b\u0438\u0433\u0440\u044b\u0432\u0430\u0435\u0442?","single_choice","A","medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,3]:\n        if n+m>=12:return True\n        if not w(n+m):return True\n    return False\nprint(1 if w(7) else 2)",
        options=["A) \u041f\u0435\u0440\u0432\u044b\u0439","B) \u0412\u0442\u043e\u0440\u043e\u0439"])
    add(19,"\u041a\u0430\u043c\u043d\u0438 *2","\u0427\u0438\u0441\u043b\u043e=3. \u0425\u043e\u0434\u044b:+1,*2. \u0426\u0435\u043b\u044c>=16. \u041a\u0442\u043e?","single_choice","A","medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for nn in [n+1,n*2]:\n        if nn>=16:return True\n        if not w(nn):return True\n    return False\nprint(1 if w(3) else 2)",
        options=["A) \u041f\u0435\u0440\u0432\u044b\u0439","B) \u0412\u0442\u043e\u0440\u043e\u0439"])
    add(19,"\u041d\u0438\u043c 3","\u041a\u0443\u0447\u0430 12. \u0425\u043e\u0434\u044b:1,2,3. \u0412\u0437\u044f\u0432\u0448\u0438\u0439 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u0432\u044b\u0438\u0433\u0440\u044b\u0432\u0430\u0435\u0442. \u041a\u0442\u043e?","single_choice","A","easy",
        options=["A) \u041f\u0435\u0440\u0432\u044b\u0439","B) \u0412\u0442\u043e\u0440\u043e\u0439"],explanation="12 mod 4 = 0. \u0412\u0442\u043e\u0440\u043e\u0439 \u0432\u044b\u0438\u0433\u0440\u044b\u0432\u0430\u0435\u0442.",
        hints=["\u041f\u0440\u0438 \u0445\u043e\u0434\u0430\u0445 1,2,3 \u2014 \u043f\u043e\u0437\u0438\u0446\u0438\u0438 \u043a\u0440\u0430\u0442\u043d\u044b\u0435 4 \u043f\u0440\u043e\u0438\u0433\u0440\u044b\u0448\u043d\u044b\u0435"])

    # TASK 20 more
    add(20,"\u0414\u0432\u0435 \u043a\u0443\u0447\u0438 +1","\u041a\u0443\u0447\u0438: 2,3. \u0425\u043e\u0434: +1 \u043a \u043b\u044e\u0431\u043e\u0439 \u043a\u0443\u0447\u0435. \u0426\u0435\u043b\u044c: \u043b\u044e\u0431\u0430\u044f \u043a\u0443\u0447\u0430 >=5. \u041a\u0442\u043e \u0432\u044b\u0438\u0433\u0440\u044b\u0432\u0430\u0435\u0442?","single_choice","A","medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(a,b):\n    if a>=5 or b>=5:return False\n    if not w(a+1,b):return True\n    if not w(a,b+1):return True\n    return False\nprint(1 if w(2,3) else 2)",
        options=["A) \u041f\u0435\u0440\u0432\u044b\u0439","B) \u0412\u0442\u043e\u0440\u043e\u0439"])
    add(20,"\u0425\u043e\u0434 *2 \u0438\u043b\u0438 +1","S=4. \u0425\u043e\u0434\u044b: +1, *2. \u0426\u0435\u043b\u044c >=20. \u041f\u0440\u0438 \u043a\u0430\u043a\u043e\u043c S \u0432\u0442\u043e\u0440\u043e\u0439 \u0432\u044b\u0438\u0433\u0440\u044b\u0432\u0430\u0435\u0442? \u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c S=4.","single_choice","B","hard","code",
        test_cases=[{"input":"","expected_output":"2","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for nn in [n+1,n*2]:\n        if nn>=20:return True\n        if not w(nn):return True\n    return False\nprint(1 if w(4) else 2)",
        options=["A) \u041f\u0435\u0440\u0432\u044b\u0439","B) \u0412\u0442\u043e\u0440\u043e\u0439"])
    add(20,"\u0413\u043b\u0443\u0431\u0438\u043d\u0430 2","S=6. \u0425\u043e\u0434\u044b:+1,+2. \u0426\u0435\u043b\u044c>=10. \u041f\u0435\u0440\u0432\u044b\u0439 \u0432\u044b\u0438\u0433\u0440\u044b\u0432\u0430\u0435\u0442 \u043d\u0430 \u043a\u0430\u043a\u043e\u043c \u0445\u043e\u0434\u0435 (1 \u0438\u043b\u0438 2)?","number",1,"medium","code",
        test_cases=[{"input":"","expected_output":"1","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,2]:\n        if n+m>=10:return True\n        if not w(n+m):return True\n    return False\n# \u041f\u0435\u0440\u0432\u044b\u0439 \u0445\u043e\u0434: \u0435\u0441\u043b\u0438 n+m>=10, \u0432\u044b\u0438\u0433\u0440\u044b\u0448 \u0437\u0430 1 \u0445\u043e\u0434\nfor m in [1,2]:\n    if 6+m>=10:\n        print(1)\n        exit()\nfor m in [1,2]:\n    nn=6+m\n    if not w(nn):\n        print(1)\n        exit()\nprint(2)")

    # TASK 21 more
    add(21,"\u0412\u0441\u0435 \u043f\u0440\u043e\u0438\u0433\u0440\u044b\u0448\u043d\u044b\u0435","\u0425\u043e\u0434\u044b:+1,+2,+3. \u0426\u0435\u043b\u044c>=15. \u041d\u0430\u0439\u0442\u0438 \u0432\u0441\u0435 S (1-14), \u0433\u0434\u0435 \u043f\u0435\u0440\u0432\u044b\u0439 \u043f\u0440\u043e\u0438\u0433\u0440\u044b\u0432\u0430\u0435\u0442.","number",0,"hard","code",
        test_cases=[{"input":"","expected_output":"4 8 12","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,2,3]:\n        if n+m>=15:return True\n        if not w(n+m):return True\n    return False\nres=[str(s) for s in range(1,15) if not w(s)]\nprint(' '.join(res))")
    add(21,"\u0412\u044b\u0438\u0433\u0440\u044b\u0448\u043d\u044b\u0439 \u0445\u043e\u0434","S=7. \u0425\u043e\u0434\u044b:+1,+3. \u0426\u0435\u043b\u044c>=12. \u041a\u0430\u043a\u0438\u043c \u0445\u043e\u0434\u043e\u043c \u043f\u0435\u0440\u0432\u044b\u0439 \u0434\u043e\u043b\u0436\u0435\u043d \u0445\u043e\u0434\u0438\u0442\u044c \u0434\u043b\u044f \u043f\u043e\u0431\u0435\u0434\u044b?","number",3,"medium","code",
        test_cases=[{"input":"","expected_output":"3","is_public":True}],
        template="from functools import lru_cache\n@lru_cache(None)\ndef w(n):\n    for m in [1,3]:\n        if n+m>=12:return True\n        if not w(n+m):return True\n    return False\nfor m in [1,3]:\n    nn=7+m\n    if nn>=12 or not w(nn):\n        print(m)\n        break")

    # TASK 22 more
    add(22,"\u041a\u0440\u0438\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043f\u0443\u0442\u044c","A(4),B(3),C(2),D(5),E(1). B \u043f\u043e\u0441\u043b\u0435 A. C \u043f\u043e\u0441\u043b\u0435 A. D \u043f\u043e\u0441\u043b\u0435 B,C. E \u043f\u043e\u0441\u043b\u0435 D. \u0412\u0440\u0435\u043c\u044f?","number",12,"medium",
        explanation="A:0-4. B:4-7. C:4-6. D:max(7,6)=7\u21927-12. E:12-13. \u041d\u043e \u0432\u043e\u043f\u0440\u043e\u0441 '\u0432\u0440\u0435\u043c\u044f'=13?... A(4)+B(3)+D(5)+E(1)=13.")
    add(22,"\u041f\u043e\u043b\u043d\u0430\u044f \u043f\u0430\u0440\u0430\u043b\u043b\u0435\u043b\u044c","5 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0432 \u043f\u043e 2\u0441, \u0432\u0441\u0435 \u043d\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u044b. \u041f\u0440\u0438 3 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0440\u0430\u0445 \u0432\u0440\u0435\u043c\u044f?","number",4,"medium",
        explanation="3 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0440\u0430: [A,B],[C,D],[E]. \u0412\u0440\u0435\u043c\u044f: max(4,4,2)=4\u0441.")
    add(22,"\u0417\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438","A(1),B(2),C(3). C \u043f\u043e\u0441\u043b\u0435 A \u0438 B. \u0412\u0440\u0435\u043c\u044f?","number",5,"easy",
        explanation="A:0-1, B:0-2, C:max(1,2)=2\u21922-5. \u0418\u0442\u043e\u0433\u043e=5.")

    # TASK 23 more
    add(23,"\u0423\u043d\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0435 \u0441\u0438\u043c\u0432\u043e\u043b\u044b","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u0443\u043d\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0445 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432 \u0432 \u0441\u0442\u0440\u043e\u043a\u0435 '\u0430\u0431\u0440\u0430\u043a\u0430\u0434\u0430\u0431\u0440\u0430'?","number",5,"easy","code",
        test_cases=[{"input":"\u0430\u0431\u0440\u0430\u043a\u0430\u0434\u0430\u0431\u0440\u0430","expected_output":"5","is_public":True}],
        template="print(len(set(input())))")
    add(23,"\u0417\u0430\u043c\u0435\u043d\u0430","\u0417\u0430\u043c\u0435\u043d\u0438\u0442\u0435 \u0432\u0441\u0435 'a' \u043d\u0430 'o' \u0432 'banana'. \u0412\u044b\u0432\u0435\u0434\u0438\u0442\u0435 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442.","number",0,"easy","code",
        test_cases=[{"input":"banana","expected_output":"bonono","is_public":True}],
        template="print(input().replace('a','o'))")
    add(23,"\u0421\u0430\u043c\u044b\u0439 \u0447\u0430\u0441\u0442\u044b\u0439","\u041d\u0430\u0439\u0442\u0438 \u0441\u0430\u043c\u044b\u0439 \u0447\u0430\u0441\u0442\u044b\u0439 \u0441\u0438\u043c\u0432\u043e\u043b \u0432 '\u0430\u0431\u0440\u0430\u043a\u0430\u0434\u0430\u0431\u0440\u0430'.","number",0,"medium","code",
        test_cases=[{"input":"\u0430\u0431\u0440\u0430\u043a\u0430\u0434\u0430\u0431\u0440\u0430","expected_output":"\u0430","is_public":True}],
        template="s=input()\nfrom collections import Counter\nprint(Counter(s).most_common(1)[0][0])")
    add(23,"\u041f\u043e\u0434\u0441\u0442\u0440\u043e\u043a\u0438 \u0434\u043b\u0438\u043d\u044b 2","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u0440\u0430\u0437\u043b\u0438\u0447\u043d\u044b\u0445 \u043f\u043e\u0434\u0441\u0442\u0440\u043e\u043a \u0434\u043b\u0438\u043d\u044b 2 \u0432 'abcabc'?","number",3,"easy","code",
        test_cases=[{"input":"abcabc","expected_output":"3","is_public":True}],
        template="s=input()\nprint(len(set(s[i:i+2] for i in range(len(s)-1))))")
    add(23,"\u0411\u0435\u0437 \u043f\u0440\u043e\u0431\u0435\u043b\u043e\u0432","\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u043f\u0440\u043e\u0431\u0435\u043b\u044b \u0438\u0437 'a b c d'. \u0412\u044b\u0432\u0435\u0441\u0442\u0438 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442.","number",0,"easy","code",
        test_cases=[{"input":"a b c d","expected_output":"abcd","is_public":True}],
        template="print(input().replace(' ',''))")

    # TASK 24 more
    add(24,"\u041f\u043e\u0434\u0441\u0447\u0451\u0442 \u0446\u0438\u0444\u0440","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u0446\u0438\u0444\u0440 \u0432 \u0441\u0442\u0440\u043e\u043a\u0435 'abc123def456'?","number",6,"easy","code",
        test_cases=[{"input":"abc123def456","expected_output":"6","is_public":True}],
        template="print(sum(1 for c in input() if c.isdigit()))")
    add(24,"\u0421\u0430\u043c\u043e\u0435 \u0434\u043b\u0438\u043d\u043d\u043e\u0435 \u0441\u043b\u043e\u0432\u043e","\u041d\u0430\u0439\u0442\u0438 \u0434\u043b\u0438\u043d\u0443 \u0441\u0430\u043c\u043e\u0433\u043e \u0434\u043b\u0438\u043d\u043d\u043e\u0433\u043e \u0441\u043b\u043e\u0432\u0430 \u0432 '\u042f \u0443\u0447\u0443 \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0442\u0438\u043a\u0443 \u0445\u043e\u0440\u043e\u0448\u043e'.","number",12,"easy","code",
        test_cases=[{"input":"\u042f \u0443\u0447\u0443 \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0442\u0438\u043a\u0443 \u0445\u043e\u0440\u043e\u0448\u043e","expected_output":"12","is_public":True}],
        template="print(max(len(w) for w in input().split()))")
    add(24,"\u041f\u0430\u043b\u0438\u043d\u0434\u0440\u043e\u043c \u0441\u0442\u0440\u043e\u043a\u0430","\u042f\u0432\u043b\u044f\u0435\u0442\u0441\u044f \u043b\u0438 '\u043a\u0430\u0437\u0430\u043a' \u043f\u0430\u043b\u0438\u043d\u0434\u0440\u043e\u043c\u043e\u043c? 1=\u0434\u0430, 0=\u043d\u0435\u0442.","number",1,"easy","code",
        test_cases=[{"input":"\u043a\u0430\u0437\u0430\u043a","expected_output":"1","is_public":True}],
        template="s=input()\nprint(1 if s==s[::-1] else 0)")
    add(24,"\u041a\u0430\u043f\u0438\u0442\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f","\u0412\u044b\u0432\u0435\u0441\u0442\u0438 \u043a\u0430\u0436\u0434\u043e\u0435 \u0441\u043b\u043e\u0432\u043e \u0441 \u0437\u0430\u0433\u043b\u0430\u0432\u043d\u043e\u0439 \u0431\u0443\u043a\u0432\u044b: '\u043f\u0440\u0438\u0432\u0435\u0442 \u043c\u0438\u0440'.","number",0,"easy","code",
        test_cases=[{"input":"\u043f\u0440\u0438\u0432\u0435\u0442 \u043c\u0438\u0440","expected_output":"\u041f\u0440\u0438\u0432\u0435\u0442 \u041c\u0438\u0440","is_public":True}],
        template="print(input().title())")
    add(24,"\u0421\u0436\u0430\u0442\u0438\u0435","\u0421\u0436\u0430\u0442\u044c \u0441\u0442\u0440\u043e\u043a\u0443: 'aaabbbcc' \u2192 'a3b3c2'.","number",0,"medium","code",
        test_cases=[{"input":"aaabbbcc","expected_output":"a3b3c2","is_public":True}],
        template="s=input()\nresult=''\ni=0\nwhile i<len(s):\n    c=s[i]\n    count=0\n    while i<len(s) and s[i]==c:\n        count+=1\n        i+=1\n    result+=c+str(count)\nprint(result)")

    # TASK 25 more
    add(25,"\u041f\u0440\u043e\u0441\u0442\u043e\u0435 \u0447\u0438\u0441\u043b\u043e","\u041d\u0430\u0438\u0431\u043e\u043b\u044c\u0448\u0435\u0435 \u043f\u0440\u043e\u0441\u0442\u043e\u0435 \u0447\u0438\u0441\u043b\u043e <= 50?","number",47,"easy","code",
        test_cases=[{"input":"","expected_output":"47","is_public":True}],
        template="def is_p(n):\n    if n<2:return False\n    for i in range(2,int(n**0.5)+1):\n        if n%i==0:return False\n    return True\nfor n in range(50,1,-1):\n    if is_p(n):\n        print(n)\n        break")
    add(25,"\u0421\u0443\u043c\u043c\u0430 \u0434\u0435\u043b\u0438\u0442\u0435\u043b\u0435\u0439","\u0421\u0443\u043c\u043c\u0430 \u0432\u0441\u0435\u0445 \u0434\u0435\u043b\u0438\u0442\u0435\u043b\u0435\u0439 \u0447\u0438\u0441\u043b\u0430 24?","number",60,"easy","code",
        test_cases=[{"input":"","expected_output":"60","is_public":True}],
        template="n=24\nprint(sum(i for i in range(1,n+1) if n%i==0))")
    add(25,"\u0412\u0437\u0430\u0438\u043c\u043d\u043e \u043f\u0440\u043e\u0441\u0442\u044b\u0435","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u0447\u0438\u0441\u0435\u043b \u043e\u0442 1 \u0434\u043e 20 \u0432\u0437\u0430\u0438\u043c\u043d\u043e \u043f\u0440\u043e\u0441\u0442\u044b \u0441 12?","number",6,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        template="from math import gcd\nprint(sum(1 for i in range(1,21) if gcd(i,12)==1))",
        explanation="\u0424\u0443\u043d\u043a\u0446\u0438\u044f \u042d\u0439\u043b\u0435\u0440\u0430: \u0447\u0438\u0441\u043b\u0430 \u0432\u0437\u0430\u0438\u043c\u043d\u043e \u043f\u0440\u043e\u0441\u0442\u044b\u0435 \u0441 12 \u043e\u0442 1 \u0434\u043e 20.")
    add(25,"\u0420\u0430\u0437\u043b\u043e\u0436\u0435\u043d\u0438\u0435","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043f\u0440\u043e\u0441\u0442\u044b\u0445 \u043c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u0435\u0439 (\u0441 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u0438\u044f\u043c\u0438) \u0443 \u0447\u0438\u0441\u043b\u0430 360?","number",6,"medium","code",
        test_cases=[{"input":"","expected_output":"6","is_public":True}],
        template="n=360\ncount=0\nd=2\nwhile d*d<=n:\n    while n%d==0:\n        count+=1\n        n//=d\n    d+=1\nif n>1:count+=1\nprint(count)",
        explanation="360=2\xb3\xd73\xb2\xd75. \u0412\u0441\u0435\u0433\u043e: 3+2+1=6 \u043c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u0435\u0439.")
    add(25,"\u0421\u043e\u0432\u0435\u0440\u0448\u0435\u043d\u043d\u044b\u0435 \u0434\u043e 10000","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u0441\u043e\u0432\u0435\u0440\u0448\u0435\u043d\u043d\u044b\u0445 \u0447\u0438\u0441\u0435\u043b \u043e\u0442 1 \u0434\u043e 10000?","number",4,"hard","code",
        test_cases=[{"input":"","expected_output":"4","is_public":True}],
        template="count=0\nfor n in range(2,10001):\n    s=sum(i for i in range(1,n) if n%i==0)\n    if s==n:count+=1\nprint(count)",
        explanation="6, 28, 496, 8128 = 4 \u0441\u043e\u0432\u0435\u0440\u0448\u0435\u043d\u043d\u044b\u0445 \u0447\u0438\u0441\u043b\u0430.")

    # TASK 26 more
    add(26,"\u0421\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0430","\u041e\u0442\u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0447\u0438\u0441\u043b\u0430 5,3,8,1,9 \u0438 \u0432\u044b\u0432\u0435\u0441\u0442\u0438 \u0447\u0435\u0440\u0435\u0437 \u043f\u0440\u043e\u0431\u0435\u043b.","number",0,"easy","code",
        test_cases=[{"input":"5\n5\n3\n8\n1\n9","expected_output":"1 3 5 8 9","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nprint(' '.join(map(str,sorted(data))))")
    add(26,"\u0423\u043d\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0435","\u041d\u0430\u0439\u0442\u0438 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0443\u043d\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0445 \u0447\u0438\u0441\u0435\u043b \u0432 \u043f\u043e\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438: 3,5,3,7,5,7,1.","number",4,"easy","code",
        test_cases=[{"input":"7\n3\n5\n3\n7\n5\n7\n1","expected_output":"4","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nprint(len(set(data)))")
    add(26,"\u0411\u043b\u0438\u0436\u0430\u0439\u0448\u0438\u0435","\u041d\u0430\u0439\u0442\u0438 \u043c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u0443\u044e \u0440\u0430\u0437\u043d\u043e\u0441\u0442\u044c \u043c\u0435\u0436\u0434\u0443 \u0441\u043e\u0441\u0435\u0434\u043d\u0438\u043c\u0438 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u0430\u043c\u0438 \u043e\u0442\u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0433\u043e \u043c\u0430\u0441\u0441\u0438\u0432\u0430: 1,5,3,8,10.","number",2,"medium","code",
        test_cases=[{"input":"5\n1\n5\n3\n8\n10","expected_output":"2","is_public":True}],
        template="n=int(input())\ndata=sorted(int(input()) for _ in range(n))\nprint(min(data[i+1]-data[i] for i in range(n-1)))")
    add(26,"K-\u0439 \u043c\u0430\u043a\u0441\u0438\u043c\u0443\u043c","3-\u0439 \u043f\u043e \u0432\u0435\u043b\u0438\u0447\u0438\u043d\u0435 \u044d\u043b\u0435\u043c\u0435\u043d\u0442 \u0438\u0437 10,3,7,5,1,8?","number",7,"medium","code",
        test_cases=[{"input":"6\n10\n3\n7\n5\n1\n8","expected_output":"7","is_public":True}],
        template="n=int(input())\ndata=sorted([int(input()) for _ in range(n)],reverse=True)\nprint(data[2])")
    add(26,"\u0421\u0443\u043c\u043c\u0430 \u043f\u0430\u0440","\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043f\u0430\u0440 (i,j), i<j, \u0442\u0430\u043a\u0438\u0445 \u0447\u0442\u043e data[i]+data[j] \u0447\u0451\u0442\u043d\u043e? \u0414\u0430\u043d\u043d\u044b\u0435: 1,2,3,4,5.","number",4,"medium","code",
        test_cases=[{"input":"5\n1\n2\n3\n4\n5","expected_output":"4","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nc=0\nfor i in range(n):\n    for j in range(i+1,n):\n        if (data[i]+data[j])%2==0:c+=1\nprint(c)",
        explanation="\u0427\u0451\u0442\u043d\u0430\u044f \u0441\u0443\u043c\u043c\u0430: \u043e\u0431\u0430 \u0447\u0451\u0442\u043d\u044b\u0435 \u0438\u043b\u0438 \u043e\u0431\u0430 \u043d\u0435\u0447\u0451\u0442\u043d\u044b\u0435. \u0427\u0451\u0442\u043d\u044b\u0435:{2,4}\u2192C(2,2)=1. \u041d\u0435\u0447\u0451\u0442\u043d\u044b\u0435:{1,3,5}\u2192C(3,2)=3. \u0418\u0442\u043e\u0433\u043e 4.")

    # TASK 27 more
    add(27,"\u0414\u0432\u0430 \u0443\u043a\u0430\u0437\u0430\u0442\u0435\u043b\u044f","\u041d\u0430\u0439\u0442\u0438 \u043f\u0430\u0440\u0443 \u0447\u0438\u0441\u0435\u043b \u0441 \u0441\u0443\u043c\u043c\u043e\u0439 15 \u0438\u0437 \u043e\u0442\u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0433\u043e \u043c\u0430\u0441\u0441\u0438\u0432\u0430: 1,3,5,7,8,10,12.","number",0,"medium","code",
        test_cases=[{"input":"7\n1\n3\n5\n7\n8\n10\n12","expected_output":"3 12","is_public":True}],
        template="n=int(input())\ndata=sorted(int(input()) for _ in range(n))\nl,r=0,n-1\nwhile l<r:\n    s=data[l]+data[r]\n    if s==15:\n        print(data[l],data[r])\n        break\n    elif s<15:l+=1\n    else:r-=1")
    add(27,"\u041d\u0430\u0438\u0431\u043e\u043b\u044c\u0448\u0438\u0439 \u0434\u0435\u043b\u044f\u0449\u0438\u0439\u0441\u044f","\u0418\u0437 \u043c\u0430\u0441\u0441\u0438\u0432\u0430 \u043d\u0430\u0439\u0442\u0438 \u043d\u0430\u0438\u0431\u043e\u043b\u044c\u0448\u0435\u0435 \u0447\u0438\u0441\u043b\u043e, \u0434\u0435\u043b\u044f\u0449\u0435\u0435\u0441\u044f \u043d\u0430 3 \u0438 \u043d\u0430 5: 10,15,30,7,25,45,9.","number",45,"easy","code",
        test_cases=[{"input":"7\n10\n15\n30\n7\n25\n45\n9","expected_output":"45","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nresult=max((x for x in data if x%3==0 and x%5==0),default=-1)\nprint(result)")
    add(27,"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0438\u043d\u0432\u0435\u0440\u0441\u0438\u0439","\u041f\u043e\u0434\u0441\u0447\u0438\u0442\u0430\u0442\u044c \u0438\u043d\u0432\u0435\u0440\u0441\u0438\u0438 (i<j, a[i]>a[j]) \u0432 \u043c\u0430\u0441\u0441\u0438\u0432\u0435 3,1,2.","number",2,"hard","code",
        test_cases=[{"input":"3\n3\n1\n2","expected_output":"2","is_public":True}],
        template="n=int(input())\na=[int(input()) for _ in range(n)]\nc=0\nfor i in range(n):\n    for j in range(i+1,n):\n        if a[i]>a[j]:c+=1\nprint(c)")
    add(27,"\u041d\u0435\u043f\u0440\u0435\u0440\u044b\u0432\u043d\u0430\u044f \u043f\u043e\u0434\u043f\u043e\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c","\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0434\u043b\u0438\u043d\u0430 \u043d\u0435\u043f\u0440\u0435\u0440\u044b\u0432\u043d\u043e\u0439 \u043f\u043e\u0434\u043f\u043e\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438 \u043f\u043e\u043b\u043e\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0445: -1,2,3,4,-2,5,6,-3.","number",3,"medium","code",
        test_cases=[{"input":"8\n-1\n2\n3\n4\n-2\n5\n6\n-3","expected_output":"3","is_public":True}],
        template="n=int(input())\ndata=[int(input()) for _ in range(n)]\nmx=cur=0\nfor x in data:\n    if x>0:cur+=1;mx=max(mx,cur)\n    else:cur=0\nprint(mx)")

    return exercises

EXTRA_EXERCISES_2 = _make_extra_exercises_2()
