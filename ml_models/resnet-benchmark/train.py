import torch
import torch.nn as nn
import torchvision
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, SubsetRandomSampler
import uuid
import numpy as np
from tqdm import tqdm
import os

BATCH_SIZE = 16
LEARNING_RATE = 0.0001
NUM_WORKERS = 1
NUM_EPOCHS = 15

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

dataset = datasets.ImageFolder('./data', transform=transform)
classes = ('Damaged', 'Not Damaged')

print("Loaded Data.....")

"""
Split: 70% train | 15% validation | 15% test
"""
dataset_size = len(dataset)
train_split = int(np.floor(0.70 * dataset_size))
val_split = train_split + int(np.floor(0.15 * dataset_size))

indices = list(range(dataset_size))
np.random.shuffle(indices)
train_idxs, val_idxs, test_idxs = indices[:train_split], indices[train_split:val_split], indices[val_split:]


train_sampler = SubsetRandomSampler(train_idxs)
val_sampler = SubsetRandomSampler(val_idxs)
test_sampler = SubsetRandomSampler(test_idxs)

print("Split Data.....")

"""
Load data
"""

trainloader = DataLoader(
    dataset, batch_size=BATCH_SIZE, sampler=train_sampler,
    num_workers=NUM_WORKERS,
)

valloader = DataLoader(
    dataset, batch_size=BATCH_SIZE, sampler=val_sampler,
    num_workers=NUM_WORKERS,
)

testloader = DataLoader(
    dataset, batch_size=BATCH_SIZE, sampler=test_sampler,
    num_workers=NUM_WORKERS,
)

print("Loaded Data Splits.....")

"""
Examine class balances in splits
"""

def view_class_balance(dataloader):
    total = 0
    not_cracked_total = 0
    for data in tqdm(dataloader):
        images, labels = data
        total += len(labels)
        not_cracked_total += sum(labels).item()

    print("There are %i examples total" % total)
    print("%i or %.2f%% are not cracked" % (not_cracked_total, (not_cracked_total / total) * 100))
    print("%i or %.2f%% are cracked" % (total - not_cracked_total, ((total - not_cracked_total) / total) * 100))
    print()

print("View class balance.....")
#view_class_balance(trainloader)
#view_class_balance(valloader)
#view_class_balance(testloader)

"""
Set up to train
"""

model = torchvision.models.resnet50().to(DEVICE)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
criterion = nn.CrossEntropyLoss()

print("Loaded Model and Optimizer.....")

"""
Train model
"""

print("Beginning to Train.....")

# Write to training log
new_id = uuid.uuid4()
f = open("./logs/train_" + str(new_id) + ".txt", "w")

for epoch in range(NUM_EPOCHS):
    print('\nSTARTING EPOCH:', epoch+1,'/',NUM_EPOCHS)
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        inputs, targets = data
        inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)

        optimizer.zero_grad()

        preds = model(inputs)
        loss = criterion(preds, targets)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()

    epoch_loss = running_loss / len(trainloader)
    log = 'Epoch: %d | loss: %.6f' % (epoch + 1, epoch_loss) + '\n'
    f.write(log)
    print(log)

    # Validation
    correct = 0
    total = 0
    with torch.no_grad():
        for data in tqdm(valloader):
            inputs, targets = data
            inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)

            preds = model(inputs)
            _, predicted = torch.max(preds.data, 1)  # max of logits

            total += targets.size(0)
            correct += (predicted == targets).sum().item()

    log = 'Validation Accuracy of the network: %d %%' % (100 * correct / total) + '\n'
    f.write(log)
    print(log)

f.close()



"""
Test model
"""

print("Beginning to test.....")

# Write to test log
f = open("./logs/test_" + str(new_id) + ".txt", "w")

correct = 0
total = 0
with torch.no_grad():
    for data in tqdm(testloader):
        inputs, targets = data
        inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)

        preds = model(inputs)
        _, predicted = torch.max(preds.data, 1)  # max of logits

        total += targets.size(0)
        correct += (predicted == targets).sum().item()

log = 'Accuracy of the network on the test images: %d %%' % (100 * correct / total) + '\n'
f.write(log)
f.close()
print(log)

torch.save(model.state_dict(), "./saved_models/" + str(new_id) +".pth")
print("Saved model:", str(new_id))
