import torch
from torch.autograd import Variable
from torchvision import transforms
from deeplabv3.model.deeplabv3 import DeepLabV3
from utils import create_sidewalk_segment, ImageFolderWithPaths

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

DEEPLAB_PRETRAINED_PATH = './deeplabv3/pretrained_models/'
IMAGES_TO_SEGMENT_PATH = './to_segment/'

deeplab_model = DeepLabV3('deeplap_1', './').to(DEVICE)

# Apply pretrained deeplab weights
deeplab_model.load_state_dict(
    torch.load(
        DEEPLAB_PRETRAINED_PATH + 'model_13_2_2_2_epoch_580.pth',
        #map_location='cpu'
    )
)

# Create evaluation set
transform = transforms.Compose([
    transforms.Resize((1024, 2048)),
    transforms.ToTensor(),
])

evalset = ImageFolderWithPaths(IMAGES_TO_SEGMENT_PATH, transform=transform)
# dataset must be a multiple of 2
evalloader = torch.utils.data.DataLoader(evalset, batch_size=2, shuffle=False, num_workers=2)

# Make predictions
preds_list = []
imgs_list = []

with torch.no_grad():
    for loaded in evalloader:
        imgs = Variable(loaded[0]).to(DEVICE)
        preds = deeplab_model(imgs)

        preds_list.append(preds)
        imgs_list.append(imgs)

i = 0
for preds, imgs in zip(preds_list, imgs_list):
    create_sidewalk_segment(preds, imgs, './segmented-images/')
