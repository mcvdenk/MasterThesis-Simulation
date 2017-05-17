import numpy as np
from rpy2.robjects import numpy2ri
from rpy2.robjects.packages import importr, data

data = np.genfromtxt('test_data.csv', delimiter=',')

numpy2ri.activate()

stats = importr('stats')
r_base = importr('base')
tam = importr('TAM')

result = tam.tam(data)

result_np = np.array(result)

print(np.array(result_np[3])[3])
print(np.array(result_np[4])[6])
print(result_np[6][0])
