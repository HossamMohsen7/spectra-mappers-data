import os
import tarfile
import os
import rasterio
from PIL import Image
import numpy as np


def extract_tar_file(tar_file_path, extract_to="data/"):
    """
    Extracts the contents of a tar file to a specified directory.

    Parameters:
    tar_file_path (str): The full path of the tar file to be extracted.
    extract_to (str): The directory where the contents of the tar file should be extracted. Default is "data/".

    Returns:
    bool: True if extraction is successful, False otherwise.
    """
    # Check if the tar file exists
    if not os.path.exists(tar_file_path):
        print(f"Error: The tar file '{tar_file_path}' does not exist.")
        return False

    # Create the extraction directory if it doesn't exist
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
        print(f"Created extraction directory: {extract_to}")

    try:
        # Open the tar file in read mode
        with tarfile.open(tar_file_path, "r") as tar_ref:
            tar_ref.extractall(
                extract_to
            )  # Extract all contents to the specified directory
        print(f"Tar file extracted successfully to {extract_to}.")
        return True
    except tarfile.TarError as e:
        # Handle tar file errors (corruption, invalid format, etc.)
        print(f"Error extracting tar file: {e}")
    except OSError as e:
        # Handle any OS-related errors (like permission issues or disk space)
        print(f"File system error during extraction: {e}")
    except Exception as e:
        # Catch-all for any other unexpected exceptions
        print(f"Unexpected error: {e}")

    return False


def convert_tif_to_grayscale_image(
    tif_file, output_format="jpeg", output_dir="converted_images"
):
    """Convert a GeoTIFF image to grayscale and save it in a different format."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create the output file path with the new extension
    output_file = os.path.join(
        output_dir, f"{os.path.splitext(os.path.basename(tif_file))[0]}.{output_format}"
    )

    try:
        # Open the TIFF image with rasterio
        with rasterio.open(tif_file) as src:
            # Read the first band of the image (assuming it's grayscale data)
            image_data = src.read(1)

        # Find the minimum and maximum values of the image data
        min_val = np.min(image_data)
        max_val = np.max(image_data)

        # Normalize the image data to 8-bit grayscale (0-255) without losing contrast
        if max_val > min_val:
            image_data_8bit = (
                (image_data - min_val) / (max_val - min_val) * 255
            ).astype(np.uint8)
        else:
            image_data_8bit = np.zeros_like(
                image_data, dtype=np.uint8
            )  # Handle uniform images

        # Convert the array data into a grayscale image
        img = Image.fromarray(image_data_8bit, mode="L")  # 'L' mode is for grayscale

        # Save the image as JPEG or WebP
        img.save(output_file, output_format.upper())
        print(f"Grayscale image converted and saved to {output_file}")

        return output_file

    except Exception as e:
        print(f"Error converting image {tif_file}: {e}")
        return None
