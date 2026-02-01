"""
Use frogleo/AI-Clothes-Changer via gradio_client API (official /infer endpoint).

  pip install gradio_client

Then run with local images or URLs:

  python run_frogleo_api.py path/to/person.png path/to/garment.png
  python run_frogleo_api.py   # uses demo URLs from Gradio docs

API (from Hugging Face Space docs):
  api_name: /infer
  person   filepath  Required  - Person Image
  garment  filepath  Required  - Garment Image
  denoise_steps  float  Default: 30
  seed     float     Default: 42
  Returns: filepath (Generated Image)
"""
import os
import sys

# Optional: for private Space
# import os; os.environ["HF_TOKEN"] = "your_token"

from gradio_client import Client, handle_file  # docs show file(); use handle_file (file is deprecated alias)


def main():
    person_arg = sys.argv[1] if len(sys.argv) > 1 else None
    garment_arg = sys.argv[2] if len(sys.argv) > 2 else None

    if person_arg and garment_arg:
        person = handle_file(person_arg)
        garment = handle_file(garment_arg)
        out_path = "frogleo_result.png"
    else:
        # Demo: use URLs from Gradio docs
        person = handle_file("https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png")
        garment = handle_file("https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png")
        out_path = "frogleo_result_demo.png"

    client = Client("frogleo/AI-Clothes-Changer")
    result = client.predict(
        person=person,
        garment=garment,
        denoise_steps=30,
        seed=42,
        api_name="/infer",
    )
    print(result)

    if result and os.path.isfile(result):
        import shutil
        shutil.copy(result, out_path)
        print(f"Saved to {out_path}")
    else:
        print("No output file returned.")


if __name__ == "__main__":
    main()
