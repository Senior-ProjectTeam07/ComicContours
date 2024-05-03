# test_st.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import torch
def test_style_vector_output(model, test_input):
    model.eval()
    with torch.no_grad():
        output = model(test_input)
    assert output.shape == (test_input.shape[0], model.output_size), "Output shape mismatch"
    assert not torch.any(torch.isnan(output)), "Output contains NaN"
    assert not torch.any(torch.isinf(output)), "Output contains Inf"
    print("Test passed: Output is valid.")