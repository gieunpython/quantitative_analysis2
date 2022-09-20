import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import factorial

def dist_binomial(n, x, p):
    combi = factorial(n)/ (factorial(x) * factorial(n-x))
    dist_prob = combi * (p**x) *((1-p)**(n-x))
    return dist_prob

fig, axes = plt.subplots(1,2, figsize=(10,4))
iteration_list = [10,60]
prob = 1/2
for idx, iteration in enumerate(iteration_list):
    prob_dist = [dist_binomial(iteration, i ,prob) for i in range(1, iteration+1)]
    sns.barplot(x=list(range(1, iteration+1)), y=prob_dist, ax=axes[idx])
    axes[idx].set_title('iteration' + str(iteration))
    axes[idx].set_xlim((iteration*prob) - 4*np.sqrt(iteration*(prob*(1-prob))), 
                        (iteration*prob) + 4*np.sqrt(iteration*prob*(1-prob)))
    axes[idx].set_xlabel('count')
plt.show()

fig, axes = plt.subplots(1,2, figsize = (10,4))

iteration_list = [120, 200]
for idx, iteration in enumerate(iteration_list):
    prob_dist = [dist_binomial(iteration, i ,prob) for i in range(1, iteration+1)]
    sns.barplot(x=list(range(1, iteration+1)), y=prob_dist, ax=axes[idx])
    axes[idx].set_title('iteration' + str(iteration))
    axes[idx].set_xlim((iteration*prob) - 4*np.sqrt(iteration*(prob*(1-prob))), 
                        (iteration*prob) + 4*np.sqrt(iteration*prob*(1-prob)))
    axes[idx].set_xlabel('count')
plt.show()
