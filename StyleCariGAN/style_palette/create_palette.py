import numpy as np

# Load the original array from the file
arr = np.load('/home/jojo/OneDrive/UNR/CS426/ComicContours/StyleCariGAN/style_palette/style_palette.npy')

# Get the 26th row as a 2D array
row_26 = arr[25:26]

# Get the 27th row as a 2D array
row_27 = arr[26:27]

# Save the 26th row to a file
np.save('style_palette_26.npy', row_26)

# Save the 27th row to a file
np.save('style_palette_27.npy', row_27)