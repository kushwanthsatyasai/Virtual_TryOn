"""
Use yisol/IDM-VTON via gradio_client API (official /tryon endpoint).

  pip install gradio_client

Then run with local images or demo URLs:

  python run_yisol_api.py path/to/person.png path/to/garment.png
  python run_yisol_api.py   # uses demo URLs from Gradio docs

API (from Hugging Face Space docs):
  api_name: /tryon
  dict(background, layers, composite)  Required  - Imageeditor
  garm_img   filepath  Required  - Garment
  garment_des  str     Required  - Textbox (e.g. "garment" or "Hello!!")
  is_checked bool  Default True
  is_checked_crop bool  Default False
  denoise_steps  float  Default 30
  seed  float  Default 42
  Returns: tuple (output_image_path, masked_image_path) – use result[0]
"""
import os
import sys

from gradio_client import Client, handle_file  # docs use file(); handle_file is the non-deprecated API


def main():
    person_arg = sys.argv[1] if len(sys.argv) > 1 else None
    garment_arg = sys.argv[2] if len(sys.argv) > 2 else None

    if person_arg and garment_arg:
        background = handle_file(person_arg)
        garm_img = handle_file(garment_arg)
        out_path = "yisol_result.png"
    else:
        url = "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
        background = handle_file(url)
        garm_img = handle_file(url)
        out_path = "yisol_result_demo.png"

    client = Client("yisol/IDM-VTON")
    result = client.predict(
        dict={
            "background": background,
            "layers": [],
            "composite": None,
        },
        garm_img=garm_img,
        garment_des="garment",
        is_checked=True,
        is_checked_crop=False,
        denoise_steps=30,
        seed=42,
        api_name="/tryon",
    )
    print(result)

    # Returns tuple of 2: [0] Output Image, [1] Masked image output
    output_file = result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else result
    if output_file and os.path.isfile(output_file):
        import shutil
        shutil.copy(output_file, out_path)
        print(f"Saved to {out_path}")
    else:
        print("No output file returned.")


if __name__ == "__main__":
    main()
