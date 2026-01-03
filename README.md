
## Live Demo

Try the FULL app demo here:

https://political-model.vercel.app/

Try the bill classifier here:  
https://politicalapp.streamlit.app/
(This demo shows the model for labelling bills)


## Pretrained Model and Training Code

This repository includes both the training scripts and the pretrained model (`model.pt`).  
You can download the pretrained model here:  
https://drive.google.com/file/d/1k0RxLq33219ElJvv8D63Ee3kUwbzRzpt/view?usp=sharing

- The training code shows how the model was built and trained from scratch.
- The pretrained model lets you skip training and run inference directly.


## Using the Pretrained Model

Use `inference.py` to make predictions on any bill summary or legislative text.  
A negative stance value means Liberal (DEM), and a positive value means Conservative (GOP).

Example:

```bash
python inference.py
