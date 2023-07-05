"""
Builds a UNet model for spike trains. 

It uses the same architecture as the original UNet paper with residual connections, but in 1D.

The input is a spike train of shape (batch_size, N_channels, Nt) and the output is a spike train of shape (batch_size, N_channels, Nt).
"""

from torch import nn


class UNet1D(nn.Module):
    def __init__(self, nlayers, dim, latent_dim):
        super(UNet1D, self).__init__()

        self.nlayers = nlayers
        self.dim = dim
        self.latent_dim = latent_dim

        self.build()

    def build(self):
        self.downsample_layers = nn.ModuleList()
        self.upsample_layers = nn.ModuleList()

        for i in range(self.nlayers):
            if i == 0:
                self.downsample_layers.append(
                    DownsampleLayer(self.dim, self.latent_dim)
                )
                self.upsample_layers.append(UpsampleLayer(self.latent_dim, self.dim))
            else:
                self.downsample_layers.append(
                    DownsampleLayer(self.latent_dim * 2**i, self.latent_dim * 2**i)
                )
                self.upsample_layers.append(
                    UpsampleLayer(self.latent_dim * 2**i, self.latent_dim * 2**i)
                )

    def forward(self, X):
        activations = []
        for layer in self.downsample_layers:
            X = layer(X)
            activations.append(X)

        X = 0
        for layer in self.upsample_layers:
            X = layer(X + activations.pop())

        return X


class DownsampleLayer(nn.Module):
    def __init__(self, in_channels, out_channels):
        self.in_channels = in_channels
        self.out_channels = out_channels

        super(DownsampleLayer, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels, out_channels, kernel_size=3, padding=1, groups=in_channels
        )
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=1, padding=1)
        self.conv3 = nn.Conv1d(
            out_channels,
            out_channels,
            kernel_size=3,
            padding=1,
            groups=in_channels,
            stride=2,
        )

        self.bn1 = nn.BatchNorm1d(out_channels)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.bn3 = nn.BatchNorm1d(out_channels)

        self.relu = nn.ReLU()

    def forward(self, X):
        X = self.conv1(X)
        X = self.bn1(X)
        X = self.relu(X)

        X = self.conv2(X)
        X = self.bn2(X)
        X = self.relu(X)

        X = self.conv3(X)
        X = self.bn3(X)
        X = self.relu(X)

        return X


class UpsampleLayer(nn.Module):
    def __init__(self, in_channels, out_channels):
        self.in_channels = in_channels
        self.out_channels = out_channels

        super(UpsampleLayer, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels, out_channels, kernel_size=3, padding=1, groups=in_channels
        )
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=1, padding=0)
        self.conv3 = nn.ConvTranspose1d(
            out_channels, out_channels, kernel_size=3, padding=1, stride=2
        )

        self.bn1 = nn.BatchNorm1d(out_channels)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.bn3 = nn.BatchNorm1d(out_channels)

        self.relu = nn.ReLU()

    def forward(self, X):
        X = self.conv1(X)
        X = self.bn1(X)
        X = self.relu(X)

        X = self.conv2(X)
        X = self.bn2(X)
        X = self.relu(X)

        X = self.conv3(X)
        X = self.bn3(X)
        X = self.relu(X)

        return X
