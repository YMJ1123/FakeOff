import torch
from torch.utils.data import Dataset, DataLoader


class DummyDataset(Dataset):
    def __init__(self, data_path='dummy_data.pt'):
        data = torch.load(data_path)
        self.x = data['x']
        self.y = data['y']
    
    def __len__(self):
        return len(self.x)
    
    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


if __name__ == '__main__':
    dataset = DummyDataset('dummy_data.pt')
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    for batch_x, batch_y in dataloader:
        print(f"Batch X shape: {batch_x.shape}, Batch Y shape: {batch_y.shape}")
        break
