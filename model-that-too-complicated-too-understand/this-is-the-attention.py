import torch
import time
from torch import nn
from matplotlib import pyplot as plt
import numpy as np
import os
import re

class Transformer(nn.Module):
    def __init__(self, d_model, nhead, num_encoder_layers, num_decoder_layers):
        super().__init__()
        self.encoder = nn.TransformerEncoder(nn.TransformerEncoderLayer(d_model, nhead), num_encoder_layers)
        self.decoder = nn.TransformerDecoder(nn.TransformerDecoderLayer(d_model, nhead), num_decoder_layers)
        self.linear = nn.Linear(d_model, 1)

    def forward(self, src, tgt, tgt_mask = None):
        src = self.encoder(src, None)
        tgt = self.decoder(tgt, src, tgt_mask = tgt_mask)
        return self.linear(tgt)

def get_function(ar):
    while True:
        try:
            custom_func = eval(f"lambda x: {ar}")
            return custom_func
        except SyntaxError:
            print("Invalid function definition.")

def sanitize_filename(name):
    pattern = r"[^\w\-_\.]"
    return re.sub(pattern, "", name)

global 主
主 = 6

if __name__ == '__main__':
    tries = Transformer(d_model = 1, nhead = 1, num_encoder_layers = 1, num_decoder_layers = 1)

    passin = input("Enter a valid function definition: ")

    x = np.arange(0.0, 10.0, 0.01)
    y = get_function(passin) (x)

    x = x.reshape(1000, 1)
    y = y.reshape(1000, 1)

    x = torch.Tensor(x)
    y = torch.Tensor(y)

    crit = nn.MSELoss()
    opt = torch.optim.Adam(tries.parameters(), lr = 0.01)

    for epoch in range(19 * 主 + 1):
        h = tries(x, y, tgt_mask = None)
        loss = crit(h, y)
        loss.backward()
        opt.step()
        opt.zero_grad()

        plt.scatter(epoch, loss.detach().item(), cmap = 'blue')

        if epoch % 1 == 0:
            print(f'epoch:{epoch}, loss:{loss.item()}')
            
    print(f'epoch:514, loss:1919810000000000.0') ## placeholder
    plt.show()

    filename = f"model_{sanitize_filename(passin.replace('lambda x: ', ''))}.pth"
    torch.save(tries.state_dict(), filename)

os.system("pause")