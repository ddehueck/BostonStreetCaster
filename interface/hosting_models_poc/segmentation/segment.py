import torch
from torchvision import transforms
from .deeplabv3.model.deeplabv3 import DeepLabV3
from .utils import create_sidewalk_segment, ImageFolderWithPaths
import os

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

FILE_ROOT = os.path.dirname(os.path.abspath(__file__))
DEEPLAB_PRETRAINED_PATH = os.path.join(FILE_ROOT, 'deeplabv3/pretrained_models')
IMAGES_TO_SEGMENT_PATH = os.path.join(FILE_ROOT, 'to_segment')
SEGMENTED_IMGS_PATH = os.path.join(FILE_ROOT, 'segmented_images/0')

deeplab_model = DeepLabV3('deeplap_1', './').to(DEVICE)

# Apply pretrained deeplab weights
deeplab_model.load_state_dict(
    torch.load(
        DEEPLAB_PRETRAINED_PATH + '/' + 'model_13_2_2_2_epoch_580.pth',
        map_location='cpu'  # Only if running on a CPU
    )
)

transform = transforms.Compose([
    transforms.Resize((1024, 2048)),
    transforms.ToTensor(),
])


def segment():
    print("Segmenting Images....")
    evalset = ImageFolderWithPaths(IMAGES_TO_SEGMENT_PATH, transform=transform)
    # NOTE: dataset must be a multiple of 2
    evalloader = torch.utils.data.DataLoader(evalset, batch_size=2, shuffle=False, num_workers=2)

    # Make predictions
    with torch.no_grad():
        for loaded in evalloader:
            paths = [path.split("/")[-1] for path in loaded[2]]
            imgs = loaded[0].to(DEVICE)
            preds = deeplab_model(imgs)

            create_sidewalk_segment(preds, imgs, SEGMENTED_IMGS_PATH + '/', paths)

            # Clear memory
            del imgs
            del preds
