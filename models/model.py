import torch
import torch.nn as nn

# Flatten Layer
class Flatten(nn.Module):
    def forward(self, input):
        return input.view(input.size(0), -1)

# Anti-Spoofing CNN Model
class AntiSpoofingModel(nn.Module):
    def __init__(self, num_classes=2):
        super(AntiSpoofingModel, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout(0.25),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout(0.25),
            nn.Conv2d(64, 128, kernel_size=3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout(0.3),
            nn.Conv2d(128, 256, kernel_size=3, padding=1), nn.BatchNorm2d(256), nn.ReLU(), nn.AdaptiveAvgPool2d((1,1)),
            Flatten()
        )
        self.classifier = nn.Sequential(
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(128, num_classes)  # ✅ No softmax here!
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Load Model Function
def load_model(model_path, device):
    model = AntiSpoofingModel(num_classes=2)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model
