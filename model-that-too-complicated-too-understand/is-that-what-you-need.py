import torch
import time
from torch import nn
from matplotlib import pyplot as plt
import NTTS
import numpy as np
import os
import re

class network(nn.Module):
    def __init__(self, k):
        super().__init__()
        self.layer1 = nn.Linear(1, k)
        self.layer2 = nn.Linear(k, 1)

    def forward(self, x):
        x = self.layer1(x)
        x = torch.sigmoid(x)
        return self.layer2(x) 

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
    tries = network(主)
    print(tries)
    print(' ')
    time.sleep(主)

    passin = input("Enter a valid function definition: ")

    x = np.arange(0.0, 10.0, 0.01)
    y = get_function(passin) (x)

    x = x.reshape(1000, 1)
    y = y.reshape(1000, 1)


    x = torch.Tensor(x)
    y = torch.Tensor(y)


    crit = nn.MSELoss()
    opt = torch.optim.Adam(tries.parameters(), lr = 0.01)

    for epoch in range(19000 * 主):
        h = tries(x)
        loss = crit(h, y)
        loss.backward()
        opt.step()
        opt.zero_grad()

        if epoch % 1000 == 0:
            print(f'epoch:{epoch}, loss:{loss.item()}')

    filename = f"model_{sanitize_filename(passin.replace('lambda x: ', ''))}.pth"
    torch.save(tries.state_dict(), filename)




print(f'epoch:114514, loss:1919810.0') # placeholder


os.system("pause")
