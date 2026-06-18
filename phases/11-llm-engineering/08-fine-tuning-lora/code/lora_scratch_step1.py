from pyexpat import model

import torch
import torch.nn as nn
import math

class LoRALayer(nn.Module):
    def __init__(self, in_features, out_features, rank=2, alpha=1.0):
        super().__init__()
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank

        self.A = nn.Parameter(torch.randn(in_features, rank) * (1 / math.sqrt(rank)))
        self.B = nn.Parameter(torch.zeros(rank, out_features))

    def forward(self, x):
        return (x @ self.A @ self.B) * self.scaling
    
class LinearWithLoRA(nn.Module):
    def __init__(self, linear, rank=2, alpha=1.0):
        super().__init__()
        self.linear = linear
        self.lora = LoRALayer(
            linear.in_features,
            linear.out_features,
            rank,
            alpha,
        )

        for param in self.linear.parameters():
            param.requires_grad = False

    def forward(self, x):
        return self.linear(x) + self.lora(x)
    
def main():
    lora = LoRALayer(4, 3)
    x = torch.randn(2, 4)
    lora_output = lora(x)

    base_linear = nn.Linear(4, 3)
    model = LinearWithLoRA(base_linear)

    x = torch.randn(2, 4)
    output = model(x)
   
    print("output shape:", tuple(output.shape))
    print("base trainable:", base_linear.weight.requires_grad)
    print("lora A trainable:", model.lora.A.requires_grad)
    print("lora B trainable:", model.lora.B.requires_grad)


if __name__ == "__main__":
    main()
