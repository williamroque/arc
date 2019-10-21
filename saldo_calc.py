from functools import reduce
from matplotlib import pyplot as plt

def bin_co(n, k):
    if(k > n - k):
        k = n - k
    r = 1
    for i in range(k):
        r = r * (n - i)
        r = r / (i + 1)
    return r

arr = [11416000.0, 11493874.17, 11572279.55, 11651219.78, 11730698.5, 11810719.38, 11891286.13, 11972402.46, 12054072.12, 12136298.89, 12219086.58, 12302438.99, 12386360.0, 12470853.47, 12555923.32, 12641573.46, 12727807.87, 12814630.53, 12902045.45, 12990056.67, 13078668.25, 13167884.3, 13257708.93, 13348146.31, 13439200.6, 13530876.02, 13623176.8, 13716107.21, 13809671.54, 13903874.13]

def calculate_saldo(row, s, i):
    return reduce(lambda a, n: a + bin_co(row, n) * s * i ** (row - n), range(row + 1))

x = range(len(arr))
y = [calculate_saldo(i, 11416000.00, 0.00682149336596227) - n for i, n in enumerate(arr)]

plt.grid()
plt.xticks(x)
plt.plot(x, y)
plt.show()
