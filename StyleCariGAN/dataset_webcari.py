# dataset_webcari.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
from PIL import Image
from torch.utils.data import Dataset


class WebCariDataset(Dataset):
    def __init__(self, path, transform):
        self.photo_list = self.load_photo_path(path)
        self.cari_list = self.load_cari_path(path)

        self.length1 = len(self.photo_list)
        self.length2 = len(self.cari_list)

        self.transform = transform

    def load_cari_path(self, path):
        cari_list = []
        for id in os.listdir(path):
            id_path = os.path.join(path, id)
            for fname in os.listdir(id_path):
                if fname.startswith('C') and fname.endswith('.jpg'):
                    file_path = os.path.join(id_path, fname)
                    cari_list.append(file_path)
        return cari_list

    def load_photo_path(self, path):
        photo_list = []
        for id in os.listdir(path):
            id_path = os.path.join(path, id)
            for fname in os.listdir(id_path):
                if fname.startswith('P') and fname.endswith('.jpg'):
                    file_path = os.path.join(id_path, fname)
                    photo_list.append(file_path)
        return photo_list

    def __len__(self):
        return max(self.length1, self.length2)

    def __getitem__(self, index):
        idx = index % self.length1
        photo = self.transform(Image.open(self.photo_list[idx]).convert('RGB'))
        idx = index % self.length2
        cari = self.transform(Image.open(self.cari_list[idx]).convert('RGB'))

        return index, photo, cari
