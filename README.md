## Pretrained Model and Training Code

This repository includes both the training scripts and the pretrained model (`model.pt`). You can install this from --> https://drive.google.com/file/d/1fk6lUQAuB0t5m_o-7Qt6Ox8wo6bU04YS/view?usp=sharing

- The **training code** is provided to ensure full reproducibility and transparency, demonstrating how the model was built and trained from scratch.
- The **pretrained model file** allows you to skip training and run inference directly.

### Using the Pretrained Model for Inference

You can use the provided `inference.py` script to make predictions on any bill summary or legislative text, then use the PDF for codes to see what it corresponds to. A negative value for stance means, Liberal(DEM) and positive means Conservative(GOP).

Example:

```bash
python inference.py
