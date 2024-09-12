#%%

import numpy as np


(1,2) in np.array([[1,3]])
# %%

np.array([[1,2]]) == np.array([[1,3]])
# %%

np.equal(np.array([[1,2]]), np.array([[1,3], [1,2]])).all(1)