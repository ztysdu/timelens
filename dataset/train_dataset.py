import os
import numpy as np
from torch.utils.data import Dataset
from torchvision import transforms
import sys
sys.path.append("..")
from timelens.common import (
    hybrid_storage,
    image_sequence,
    os_tools,
    pytorch_tools,
    transformers
)
from PIL import Image

class TrainData(Dataset):
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.sample = self._make_sample()
        self.transform_list = transformers.initialize_transformers()
        
        # print(len(self.sample))

        
    
    def __len__(self):
        return len(self.sample)
    
    
    def _make_sample(self):
        sample = []
        for each_first_level_dir in sorted(os.listdir(self.root_dir)):
            first_level_path = os.path.join(self.root_dir, each_first_level_dir)
            for each_second_level_dir in sorted(os.listdir(first_level_path)):
                class_name = os.path.join(each_first_level_dir, each_second_level_dir)
                sample.append(class_name)
        return sample
    

    def __getitem__(self, idx):
        
        class_name = self.sample[idx]
        
        gts=[]
        
        event_folder_path=os.path.join(self.root_dir, class_name, 'events')
        image_folder_path=os.path.join(self.root_dir,class_name,'images')
        gt_path=os.path.join(self.root_dir,class_name,'gt')
            
        
        sample = {'image': image_folder_path,'event': event_folder_path, 'gt': gt_path, 'class_name': class_name}
        
        return sample
        
        


