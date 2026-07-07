# AIRS Sprint 1 model definitions - load checkpoints saved by the training notebook.
from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

NUM_CLASSES = 3
EMB_DIM = 512


class TabularAttentionModel(nn.Module):
    def __init__(self, n_features=9, d_model=128, n_heads=4, n_classes=NUM_CLASSES, dropout=0.2):
        super().__init__()
        self.feature_embed = nn.Linear(1, d_model)
        self.attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=n_heads, dropout=dropout, batch_first=True)
        self.attn_norm = nn.LayerNorm(d_model)
        self.classifier = nn.Sequential(
            nn.Linear(n_features * d_model, 256), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(256, 64), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(64, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, N = x.shape
        tokens = self.feature_embed(x.unsqueeze(-1))
        attn_out, _ = self.attn(tokens, tokens, tokens)
        tokens = self.attn_norm(tokens + attn_out)
        return self.classifier(tokens.reshape(B, -1))


class AcousticMLP(nn.Module):
    def __init__(self, emb_dim=EMB_DIM, modalities='both', n_classes=NUM_CLASSES, dropout=0.2):
        super().__init__()
        self.modalities = modalities
        in_dim = emb_dim if modalities != 'both' else emb_dim * 2
        self.net = nn.Sequential(
            nn.Linear(in_dim, 512), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(512, 256), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(256, 64), nn.GELU(), nn.Dropout(dropout),
        )
        self.classifier = nn.Linear(64, n_classes)

    def forward(self, cough_emb, vowel_emb):
        if self.modalities == 'cough_only':
            x = cough_emb
        elif self.modalities == 'vowel_only':
            x = vowel_emb
        else:
            x = torch.cat([cough_emb, vowel_emb], dim=-1)
        return self.classifier(self.net(x))


class LateFusionClassical(nn.Module):
    def __init__(self, n_tab=9, emb_dim=EMB_DIM, fusion_d=64, n_classes=NUM_CLASSES, dropout=0.2):
        super().__init__()
        self.tab_branch = nn.Sequential(
            nn.Linear(n_tab, 64), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(64, 128), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(128, fusion_d), nn.GELU(),
        )
        self.acoustic_branch = nn.Sequential(
            nn.Linear(emb_dim * 2, 256), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(256, 128), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(128, fusion_d), nn.GELU(),
        )
        self.fusion_head = nn.Sequential(
            nn.Linear(fusion_d * 2, 64), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(64, n_classes),
        )

    def forward(self, tab, cough_emb, vowel_emb):
        tab_feat = self.tab_branch(tab)
        acoustic_feat = self.acoustic_branch(torch.cat([cough_emb, vowel_emb], dim=-1))
        return self.fusion_head(torch.cat([tab_feat, acoustic_feat], dim=-1))


class AudioFrameProjector(nn.Module):
    def __init__(self, frame_len=640, d_model=256):
        super().__init__()
        self.frame_len = frame_len
        self.projection = nn.Linear(frame_len, d_model)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, waveform):
        B, T = waveform.shape
        n_frames = T // self.frame_len
        waveform = waveform[:, :n_frames * self.frame_len]
        frames = waveform.reshape(B, n_frames, self.frame_len)
        return self.norm(self.projection(frames))


class TabularTokenizer(nn.Module):
    def __init__(self, n_features=9, d_model=256, mode='per_feature'):
        super().__init__()
        self.mode = mode
        if mode == 'single':
            self.proj = nn.Sequential(nn.Linear(n_features, d_model), nn.LayerNorm(d_model))
        else:
            self.proj = nn.Linear(1, d_model)
            self.norm = nn.LayerNorm(d_model)

    def forward(self, x):
        if self.mode == 'single':
            return self.proj(x).unsqueeze(1)
        tokens = self.proj(x.unsqueeze(-1))
        return self.norm(tokens)


class EncoderFreeUnifiedModel(nn.Module):
    MODALITY_COUGH = 0
    MODALITY_VOWEL = 1
    MODALITY_TABULAR = 2
    MODALITY_EMB_PRIOR = 3

    def __init__(
        self,
        d_model=256,
        n_heads=8,
        n_layers=4,
        n_tab_features=9,
        frame_len=640,
        max_cough_frames=375,
        max_vowel_frames=150,
        emb_dim=EMB_DIM,
        n_classes=NUM_CLASSES,
        dropout=0.1,
        use_emb_residuals=True,
        tab_mode='per_feature',
    ):
        super().__init__()
        self.d_model = d_model
        self.use_emb_residuals = use_emb_residuals
        self.cough_proj = AudioFrameProjector(frame_len, d_model)
        self.vowel_proj = AudioFrameProjector(frame_len, d_model)
        self.tab_proj = TabularTokenizer(n_tab_features, d_model, mode=tab_mode)
        if use_emb_residuals:
            self.cough_emb_proj = nn.Sequential(nn.Linear(emb_dim, d_model), nn.LayerNorm(d_model))
            self.vowel_emb_proj = nn.Sequential(nn.Linear(emb_dim, d_model), nn.LayerNorm(d_model))
        self.modality_embed = nn.Embedding(4, d_model)
        max_tokens = max_cough_frames + max_vowel_frames + n_tab_features + 2
        self.pos_embed = nn.Embedding(max_tokens + 10, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=4 * d_model,
            dropout=dropout, activation='gelu', batch_first=True, norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers, norm=nn.LayerNorm(d_model))
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(d_model // 2, n_classes),
        )

    def forward(self, tab, cough_wav=None, vowel_wav=None, cough_emb=None, vowel_emb=None):
        B = tab.shape[0]
        token_list, type_list = [], []
        tab_tokens = self.tab_proj(tab)
        token_list.append(tab_tokens)
        type_list.append(torch.full((B, tab_tokens.shape[1]), self.MODALITY_TABULAR, dtype=torch.long, device=tab.device))
        if cough_wav is not None:
            cough_tokens = self.cough_proj(cough_wav)
            token_list.append(cough_tokens)
            type_list.append(torch.full((B, cough_tokens.shape[1]), self.MODALITY_COUGH, dtype=torch.long, device=tab.device))
        if vowel_wav is not None:
            vowel_tokens = self.vowel_proj(vowel_wav)
            token_list.append(vowel_tokens)
            type_list.append(torch.full((B, vowel_tokens.shape[1]), self.MODALITY_VOWEL, dtype=torch.long, device=tab.device))
        if self.use_emb_residuals and cough_emb is not None:
            token_list.append(self.cough_emb_proj(cough_emb).unsqueeze(1))
            type_list.append(torch.full((B, 1), self.MODALITY_EMB_PRIOR, dtype=torch.long, device=tab.device))
        if self.use_emb_residuals and vowel_emb is not None:
            token_list.append(self.vowel_emb_proj(vowel_emb).unsqueeze(1))
            type_list.append(torch.full((B, 1), self.MODALITY_EMB_PRIOR, dtype=torch.long, device=tab.device))
        tokens = torch.cat(token_list, dim=1)
        types = torch.cat(type_list, dim=1)
        pos = torch.arange(tokens.shape[1], device=tab.device).unsqueeze(0).expand(B, -1)
        tokens = tokens + self.modality_embed(types) + self.pos_embed(pos)
        pooled = self.transformer(tokens).mean(dim=1)
        return self.classifier(pooled)


MODEL_REGISTRY = {
    'TabularAttentionModel': TabularAttentionModel,
    'AcousticMLP': AcousticMLP,
    'LateFusionClassical': LateFusionClassical,
    'EncoderFreeUnifiedModel': EncoderFreeUnifiedModel,
}


def load_model(config_path, weights_path, map_location='cpu'):
    import json
    with open(config_path, encoding='utf-8') as f:
        config = json.load(f)
    cls = MODEL_REGISTRY[config['model_class']]
    model = cls(**config['model_kwargs'])
    model.load_state_dict(torch.load(weights_path, map_location=map_location))
    model.eval()
    return model, config
