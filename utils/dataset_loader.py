import pytorch_lightning as L
import os
import torch
from torch.utils.data import Dataset, DataLoader
import h5py
import random
import numpy as np

# Random sampler from dataset.
def random_batch_sampler(dataset: Dataset, size: int):
    prevs = []
    currs = []
    for _ in range(size):
        rnd_idx = random.randint(0, len(dataset)-1)
        sample = dataset[rnd_idx]
        prev, curr = sample
        prevs.append(prev)
        currs.append(curr)

    batch = torch.from_numpy(np.array([prevs, currs]))
    return batch
    

# Define the MaestroV3DataSet.
class MaestroV3DataSet(Dataset):

    def __init__(self, file_path: str, mode: str = "single"):
        # Store the file path
        self.h5_path = file_path
        # Save dataset length.
        with h5py.File(self.h5_path, "r") as f:
            self.length = len(f['x'])
        # Mode can be either single or pair.
        assert mode == "single" or mode == "pair"

        # Save mode.
        self.mode = mode

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        with h5py.File(self.h5_path, 'r') as db:
            if self.mode == "single":
                # MODEL 1
                sample = db['x'][idx]
                sample = torch.tensor(sample, dtype=torch.float32) # [128, 16]
                sample = sample.unsqueeze(0) # [1, 128, 16]
                return sample
    
            else:
                # MODEL 2
                prev, curr = db['x'][idx]
    
                prev = torch.tensor(prev, dtype=torch.float32) # [128, 16]
                curr = torch.tensor(curr, dtype=torch.float32) # [128, 16]
    
                prev = prev.unsqueeze(0) # [1, 128, 16]
                curr = curr.unsqueeze(0) # [1, 128, 16]
                
                return prev, curr


# Define the meastro DataLoader.
class MaestroV3DataModule(L.LightningDataModule):

    def __init__(self, data_dir: str, batch_size: int = 32, mode: str = "single"):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.mode = mode

    def setup(self, stage: str):
        self.dataset = MaestroV3DataSet(self.data_dir, self.mode)

    def train_dataloader(self):
        nw = 9 # Shuld be tuned based on the CPU.
        return DataLoader(self.dataset, batch_size=self.batch_size, shuffle=True,
                         num_workers=nw)
