# TektonAI/models/anfis.py
import torch
import torch.nn as nn

class ANFISNetwork(nn.Module):
    def __init__(self, input_dim=4, hidden_layers=[32, 16]):
        super().__init__()
        layers = []
        in_dim = input_dim
        for h_dim in hidden_layers:
            layers.append(nn.Linear(in_dim, h_dim))
            layers.append(nn.Tanh())
            in_dim = h_dim
        layers.append(nn.Linear(in_dim, 1))
        layers.append(nn.Sigmoid())
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)