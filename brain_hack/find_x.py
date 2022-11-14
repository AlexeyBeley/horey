"""
Checking some new features
"""
x = "123456789"
print(type(x))
# >>> <class 'str'>
print(x[::2])
# >>> 13579
print(x[-2::-2])
# >>> 8642


x = "1_2_3_3_2_1"
print(type(x))
# >>> <class 'str'>
print(int(x))
# >>> 123321
print(len(x))
# >>> 11

x = list(range(10))
print(type(x))
# >>> <class 'list'>
x[1::3] = [0] * 3
print(x)
# >>> [0, 0, 2, 3, 0, 5, 6, 0, 8, 9]


x = "555666777"
print(x[::-1])


# print(x)
# if (x := len(x)) == 10:
#    print(True)
# x = 1
# y = (x := 2)
# print(x, y)
