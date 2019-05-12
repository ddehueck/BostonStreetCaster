import torch
import torchvision
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import os


FILE_ROOT = os.path.dirname(os.path.abspath(__file__))

MODEL_FILE = '05d0e533-13bc-4fe3-b8ed-35550210a37c.pth'
PRETRAINED_CLASSIFIER = os.path.join(FILE_ROOT, 'saved_models/' + MODEL_FILE)
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'segmentation/segmented_images'))

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

classes = ('Damaged', 'Not Damaged')

model = torchvision.models.resnet50().to(DEVICE)
model.load_state_dict(torch.load(PRETRAINED_CLASSIFIER,  map_location='cpu'))


def classify():
    evalset = datasets.ImageFolder(DATA_PATH, transform=transform)
    # NOTE: dataset must be a multiple of 2
    evalloader = torch.utils.data.DataLoader(evalset, batch_size=2, shuffle=False, num_workers=2)

    predictions = []
    with torch.no_grad():
        for data in evalloader:
            inputs, targets = data
            inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)

            preds = model(inputs)
            _, predicted = torch.max(preds.data, 1)  # max of logits

            for e in predicted:
                predictions.append(classes[e.item()])

    return predictions

