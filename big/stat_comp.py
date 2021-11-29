import numpy as np
import joblib
import math

data=joblib.load("comp_res.pkl")

alg_names = "nx_christofides", "nx_greedy", "random_path", "deliberately_bad", "google_generic_tabu_search", "google_greedy_descent", "google_guided_local_search", "google_simulated_annealing", "google_tabu_search",


for key, d in data.items():
    print(key)
    d = np.array(d)
    case_min = d.min(axis=1)
    frac = (d.T/case_min).T
    mean_score = (frac.mean(axis=0)-1)*100
    order = np.argsort(mean_score)
    for i in order:
        score = mean_score[i]
        # if score==0: score="best"
        # else: score=math.log10(score)
        print(alg_names[i], f"{score:.2f}", "%")
