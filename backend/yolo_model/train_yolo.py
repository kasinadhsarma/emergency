import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.rpn import AnchorGenerator
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import functional as F
from PIL import Image
import os

# Define the dataset class
class EmergencyVehicleDataset(Dataset):
    def __init__(self, root, transforms=None):
        self.root = root
        self.transforms = transforms
        self.imgs = list(sorted(os.listdir(os.path.join(root, "Ambulance"))))
        self.imgs += list(sorted(os.listdir(os.path.join(root, "Fire Engine"))))
        self.imgs += list(sorted(os.listdir(os.path.join(root, "Police"))))
        self.imgs += list(sorted(os.listdir(os.path.join(root, "Non Emergency"))))

    def __getitem__(self, idx):
        img_path = os.path.join(self.root, self.imgs[idx])
        img = Image.open(img_path).convert("RGB")
        if self.transforms:
            img = self.transforms(img)
        # Add labels for each image
        label = self.get_label(img_path)
        return img, label

    def __len__(self):
        return len(self.imgs)

    def get_label(self, img_path):
        if "Ambulance" in img_path:
            return 1  # Label for ambulance
        elif "Fire Engine" in img_path:
            return 2  # Label for fire engine
        elif "Police" in img_path:
            return 3  # Label for police
        else:
            return 0  # Label for non-emergency

# Define the transformations
def get_transform(train):
    transforms = []
    transforms.append(F.ToTensor())
    if train:
        transforms.append(F.RandomHorizontalFlip(0.5))
    return F.Compose(transforms)

# Load the dataset
dataset = EmergencyVehicleDataset(root="backend/Dataset", transforms=get_transform(train=True))
dataset_test = EmergencyVehicleDataset(root="backend/Dataset", transforms=get_transform(train=False))

# Define the data loaders
data_loader = DataLoader(dataset, batch_size=2, shuffle=True, num_workers=4, collate_fn=lambda x: tuple(zip(*x)))
data_loader_test = DataLoader(dataset_test, batch_size=2, shuffle=False, num_workers=4, collate_fn=lambda x: tuple(zip(*x)))

# Load the pre-trained model
model = fasterrcnn_resnet50_fpn(pretrained=True)

# Define the optimizer
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)

# Define the learning rate scheduler
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

# Train the model
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    for images, targets in data_loader:
        images = list(image for image in images)
        targets = [{k: v for k, v in t.items()} for t in targets]
        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())
        optimizer.zero_grad()
        losses.backward()
        optimizer.step()
    lr_scheduler.step()

# Save the trained model
torch.save(model.state_dict(), "backend/yolo_model/yolo_model.pth")
