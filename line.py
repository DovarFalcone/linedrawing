import cv2
import os
import imageio
import streamlit as st
import numpy as np

st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("Line Drawing App")

# Define the input and output file paths
input_path = st.file_uploader("Upload input image", type=['jpg', 'jpeg', 'png'])
if input_path is None:
    input_image = cv2.imread('amigo.jpg')
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
else:
    # Load the input image
    input_image = cv2.imdecode(np.fromstring(input_path.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)


image_output_dir = 'images'
output_dir = 'output'
output_filename = 'output_gif.gif'

# Define the parameters for the edge-preserving smoothing
with st.sidebar:
    st.subheader("Parameters")
    bilateral_diameter = st.slider("Bilateral diameter", 1, 50, 15)
    bilateral_sigma_color = st.slider("Bilateral sigma color", 1, 500, 150)
    bilateral_sigma_space = st.slider("Bilateral sigma space", 1, 500, 150)

    # Define the parameters for the Gaussian blur
    gaussian_kernel_size = st.slider("Gaussian kernel size", 1, 50, 15, step=2)
    gaussian_sigma = st.slider("Gaussian sigma", 0, 50, 0)

    # Define the parameters for the Canny edge detection
    canny_threshold1 = st.slider("Canny threshold1", 1, 1000, 200)
    canny_threshold2 = st.slider("Canny threshold2", 1, 1000, 400)


# Create a list of images
images = [input_image]

# Apply edge-preserving smoothing using Bilateral Filter
edge_preserving_image = cv2.bilateralFilter(input_image, bilateral_diameter, bilateral_sigma_color, bilateral_sigma_space)
images.append(edge_preserving_image)

# Convert the edge-preserving image to grayscale
gray_image = cv2.cvtColor(edge_preserving_image, cv2.COLOR_BGR2GRAY)

# Invert the grayscale image
inverted_image = 255 - gray_image


# Apply Gaussian blur with larger kernel size
blurred_image = cv2.GaussianBlur(inverted_image, (gaussian_kernel_size, gaussian_kernel_size), gaussian_sigma)
images.append(blurred_image)

# Invert the blurred image
inverted_blurred_image = 255 - blurred_image

# Create the pencil sketch image
pencil_sketch_image = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)
images.append(pencil_sketch_image)

# Create the continuous line drawing image with lower threshold
continuous_line_drawing = cv2.Canny(pencil_sketch_image, canny_threshold1, canny_threshold2)
images.append(continuous_line_drawing)

# Save the generated images in the output directory
for i, image in enumerate(images):
    output_path = os.path.join(image_output_dir, f'output_image{i}.png')
    cv2.imwrite(output_path, image)

# Use imageio to create a GIF from the generated images and save it in the output directory
output_path = os.path.join(output_dir, output_filename)
imageio.mimsave(output_path, images, fps=1)

# Display the input and output images
input_col, output_col = st.columns(2)

with input_col:
    st.image(input_image, caption='Input Image', use_column_width=True)

with output_col:
    for i, image in enumerate(reversed(images[1:])):
        st.image(image, caption=f'Output Image {len(images)-i}', use_column_width=True)

# Display the generated GIF
gif_col = st.empty()
with gif_col:
    st.write("Generating GIF...")
    with open(output_path, 'rb') as f:
        gif_bytes = f.read()
    st.image(gif_bytes, caption='Generated GIF', use_column_width=True)
