#%%
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import math
import numpy as np
import matplotlib.pyplot as plt

dtype = torch.float32
if torch.cuda.is_available():
  device = torch.device('cuda')
  torch.set_default_dtype(torch.cuda.FloatTensor)
else:
  device = torch.device("mps")
  torch.set_default_dtype(torch.float32)

to_nearest_64 = lambda x: round(x/64) * 64
model_scale = 1.
max_seq_len = 200

qk_dim_div = 8
expand_factor = 2
residual_depth = to_nearest_64(384 * math.log2(1.+model_scale))

num_blocks = round(8 * math.log2(1.+model_scale))
causal_mask = torch.triu(torch.ones(max_seq_len, max_seq_len), diagonal=1).bool()

with torch.no_grad():
  bias_range = torch.arange(-max_seq_len+1, 1).to(device, dtype)
  position_bias_base = bias_range.unsqueeze(0) - bias_range.unsqueeze(1)
  negative_infinity_matrix_base = torch.empty_like(position_bias_base).fill_(-float("inf"))
  causal_mask = torch.tril(torch.ones((max_seq_len, max_seq_len), device=device, dtype=torch.bool))

#%%

class LatentAttentionBlock(nn.Module):
  """ Efficient fused latent-space attention block. Linear keys and queries, nonlinear values."""
  def __init__(self, num_dim):
    super().__init__()
    self.dim        = num_dim
    self.qk_dim     = self.dim//qk_dim_div
    self.v_dim      = num_dim
    self.expand_dim = num_dim * expand_factor
    self.norm       = nn.LayerNorm(self.dim)
    self.expand     = nn.Parameter(.5 * 1./residual_depth**.5 * 1./expand_factor * torch.randn(2*self.qk_dim+2*self.expand_dim, self.dim))
    self.project    = nn.Parameter(1. * 1./residual_depth**.5 * 1./expand_factor * 1./num_blocks * torch.randn((self.dim, self.expand_dim),dtype=dtype))
    self.position_bias_mult = nn.Parameter(torch.tensor(1.))
    self.dropout = nn.Dropout(0.2)

  def forward(self, x):
  
    residual = x
    attn_mask = torch.where(causal_mask[:x.shape[1], :x.shape[1]], F.softplus(self.position_bias_mult) * position_bias_base[:x.shape[1], :x.shape[1]], negative_infinity_matrix_base[:x.shape[1], :x.shape[1]])
    x = self.norm(x)
    x = self.dropout(F.linear(x, self.expand))
    query, key, linear, pre_gelu = x.split((self.qk_dim, self.qk_dim, self.expand_dim, self.expand_dim), dim=-1)
    geglu = linear * F.gelu(pre_gelu)
    geglu_local, geglu_attention_value = geglu.split((self.expand_dim-self.v_dim, self.v_dim), -1)
    attention = F.scaled_dot_product_attention(query, key, geglu_attention_value, attn_mask=attn_mask)
    out = F.linear(torch.cat([geglu_local, attention], dim=-1), self.project)
    x = residual + out
    return x

  def inference(self, x, k, v):
    residual = x
    mask_shape = (x.shape[1], x.shape[1] + k.shape[1])
    attn_mask = torch.where(causal_mask[:x.shape[1], :x.shape[1]], F.softplus(self.position_bias_mult) * position_bias_base[:mask_shape[0], :mask_shape[1]], negative_infinity_matrix_base[:mask_shape[0], :mask_shape[1]])
    x = self.norm(x)
    x = self.dropout(F.linear(x, self.expand))
    query, key, linear, pre_gelu = x.split((self.qk_dim, self.qk_dim, self.expand_dim, self.expand_dim), dim=-1)
    geglu = linear * F.gelu(pre_gelu)
    geglu_local, geglu_attention_value = geglu.split((self.expand_dim-self.v_dim, self.v_dim), -1)
    key = torch.cat([k, key], dim=1)
    v = torch.cat([v, geglu_attention_value], dim=1)
    attention = F.scaled_dot_product_attention(query, key, v, attn_mask=attn_mask)
    out = F.linear(torch.cat([geglu_local, attention], dim=-1), self.project)
    x = residual + out
    return x, key, geglu_attention_value

n_pos = 64
n_piece = 7 # 0 = empty

class Model(nn.Module):
  def __init__(self):
    super().__init__()
    self.timeemb = nn.Parameter(torch.randn(max_seq_len, residual_depth)/residual_depth**.5)
    self.posemb = nn.Embedding(n_pos, residual_depth, scale_grad_by_freq=True)
    self.pieceemb = nn.Embedding(n_piece, residual_depth, scale_grad_by_freq=True)
    self.norm = nn.LayerNorm(residual_depth)
    self.blocks:list[LatentAttentionBlock] = nn.ModuleList([LatentAttentionBlock(residual_depth) for _ in range(num_blocks)])
    self.norm2 = nn.LayerNorm(residual_depth)
    self.winprob = nn.Sequential(nn.Linear(residual_depth, 256), nn.GELU(), nn.Linear(256, 3))

  def out(self, x): return torch.matmul(x, self.posemb.weight.t())

  def forward(self, xpos, xpiece):

    x = self.posemb(xpos) + self.pieceemb(xpiece) 
    x += self.timeemb.unsqueeze(0)[:,:xpos.shape[1]]
    x = self.norm(x)
    for block in self.blocks: x = block(x)
    x = self.norm2(x)
    return self.out(x), self.winprob(x)
  
  def inference(self, xpos, xpiece, k, v):
    x = self.posemb(xpos) + self.pieceemb(xpiece) + self.timeemb.unsqueeze(0)[:,:xpos.shape[1]]
    x = self.norm(x)
    KK = []
    VV = []
    for block, ki, vi in zip(self.blocks, k, v):
      x, kk, vv = block.inference(x, ki, vi)
      KK.append(kk)
      VV.append(vv)

    x = self.norm2(x)
    return self.out(x), self.winprob(x), KK, VV

def pretrained():
  model = Model().to(device)
  model.load_state_dict(torch.load('tinychess/training/model.pth'))
  return model

#%%
if __name__ == '__main__':
  B = 2
  xpos = torch.randint(0, n_pos, (B, max_seq_len)).to(device)
  xpiece = torch.randint(0, n_piece, (B, max_seq_len)).to(device)
  model = Model().to(device)
  policy, win = model(xpos, xpiece)