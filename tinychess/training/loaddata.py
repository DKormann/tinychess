#%%
import numpy as np

datapath = "./dataset/moves2000+.npz"

data = np.load(datapath)


print(data.files)
print(data['moves'].shape)
print(data['wins'].shape)

