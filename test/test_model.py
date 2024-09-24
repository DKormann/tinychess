from tinychess.training.model import pretrained, device
import torch


def tensor(x): return torch.tensor(x).to(device)

model = pretrained()

model.eval()
pol, eval = model(tensor([[0, 52]]), tensor([[0, 0]]))

def inferloop(pos, piece):

  k = [torch.zeros((1, 0, 48)).to(device, torch.long) for _ in range(len(model.blocks))]
  v = [torch.zeros((1, 0, 384)).to(device, torch.long) for _ in range(len(model.blocks))]
  for po, pi in zip(pos, piece):
    pol, eval, k, v = model.inference(tensor([[po]]), tensor([[pi]]), k, v)
    yield pol.argmax(-1).item()


assert list(inferloop([0, 52], [0, 0])) == [52, 36]
