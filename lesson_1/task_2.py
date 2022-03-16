"""
2. Каждое из слов «class», «function», «method» записать в байтовом типе.
Сделать это необходимо в автоматическом, а не ручном режиме,
с помощью добавления литеры b к текстовому значению,
(т.е. ни в коем случае не используя методы encode, decode или функцию bytes)
и определить тип, содержимое и длину соответствующих переменных.
"""

VAR_1 = 'class'
VAR_2 = 'function'
VAR_3 = 'method'

STR = [VAR_1, VAR_2, VAR_3]
for value in STR:
    val = eval(f"b'{value}'")
    print(val)
    print(type(val))
    print(len(val))
