"""
Minimal standalone test: call Gradio Space directly (no FastAPI, no app services).
Run from backend/:  python test_gradio_direct.py [person.png] [cloth.png]
If no args, creates small test images in temp/uploads and uses those.
"""
import os
import sys

# Ensure we can import app and use backend cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    from gradio_client import Client, handle_file

    # Resolve input images
    if len(sys.argv) >= 3:
        person_path = os.path.abspath(sys.argv[1])
        cloth_path = os.path.abspath(sys.argv[2])
    else:
        # Create minimal test images if temp/uploads exists
        os.makedirs("temp/uploads", exist_ok=True)
        from PIL import Image
        person_path = "temp/uploads/direct_test_person.png"
        cloth_path = "temp/uploads/direct_test_cloth.png"
        Image.new("RGB", (256, 384), color=(200, 180, 160)).save(person_path)
        Image.new("RGB", (256, 384), color=(80, 120, 200)).save(cloth_path)
        print(f"Created test images: {person_path}, {cloth_path}")

    if not os.path.isfile(person_path) or not os.path.isfile(cloth_path):
        print("Usage: python test_gradio_direct.py <person_image> <cloth_image>")
        sys.exit(1)

    seed = 42
    denoise_steps = 30

    # 1) Try frogleo/AI-Clothes-Changer (same call as in FastAPI path)
    print("=" * 60)
    print("1) Calling frogleo/AI-Clothes-Changer (no FastAPI)")
    print("=" * 60)
    try:
        client = Client("frogleo/AI-Clothes-Changer")
        result = client.predict(
            person=handle_file(person_path),
            garment=handle_file(cloth_path),
            denoise_steps=denoise_steps,
            seed=seed,
            api_name="/infer",
        )
        print("frogleo predict() returned:", type(result).__name__, repr(result)[:200])
        if result and os.path.isfile(result):
            out = "temp/results/direct_frogleo_result.png"
            os.makedirs("temp/results", exist_ok=True)
            import shutil
            shutil.copy(result, out)
            print("SUCCESS. Saved to", out)
        else:
            print("frogleo returned no file:", result)
    except Exception as e:
        print("frogleo FAILED:", e)
        import traceback
        traceback.print_exc()

    # 2) Try Kwai-Kolors/Kolors-Virtual-Try-On (fallback)
    print()
    print("=" * 60)
    print("2) Calling Kwai-Kolors/Kolors-Virtual-Try-On (no FastAPI)")
    print("=" * 60)
    try:
        client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")
        result = client.predict(
            handle_file(person_path),
            handle_file(cloth_path),
            seed,
            False,
            fn_index=0,
        )
        print("Kolors predict() returned:", type(result).__name__)
        if isinstance(result, (list, tuple)):
            print("  len:", len(result), "first type:", type(result[0]).__name__ if result else "N/A")
            if len(result) > 0:
                result_path = result[0]
                print("  result[0]:", repr(result_path)[:120])
                if result_path and os.path.isfile(result_path):
                    out = "temp/results/direct_kolors_result.png"
                    os.makedirs("temp/results", exist_ok=True)
                    import shutil
                    shutil.copy(result_path, out)
                    print("SUCCESS. Saved to", out)
                else:
                    print("Kolors result[0] is not a valid file:", result_path)
            else:
                print("Kolors returned empty list/tuple")
        else:
            print("  raw:", repr(result)[:200])
            if result and os.path.isfile(result):
                out = "temp/results/direct_kolors_result.png"
                os.makedirs("temp/results", exist_ok=True)
                import shutil
                shutil.copy(result, out)
                print("SUCCESS. Saved to", out)
    except Exception as e:
        print("Kolors FAILED:", e)
        import traceback
        traceback.print_exc()

    # 3) Try yisol/IDM-VTON (has named api "tryon", often more stable)
    print()
    print("=" * 60)
    print("3) Calling yisol/IDM-VTON (api_name=tryon)")
    print("=" * 60)
    try:
        from PIL import Image
        client = Client("yisol/IDM-VTON")
        # yisol expects 768x1024; resize test images in place
        for p in (person_path, cloth_path):
            with Image.open(p) as im:
                im = im.convert("RGB").resize((768, 1024), Image.Resampling.LANCZOS)
                im.save(p)
        imgs_value = {"background": handle_file(person_path), "layers": None, "composite": None}
        result = client.predict(
            imgs_value,
            handle_file(cloth_path),
            "garment",
            True,
            False,
            30,
            seed,
            api_name="/tryon",
        )
        out_path = result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else result
        if out_path and os.path.isfile(out_path):
            out = "temp/results/direct_yisol_result.png"
            os.makedirs("temp/results", exist_ok=True)
            import shutil
            shutil.copy(out_path, out)
            print("yisol SUCCESS. Saved to", out)
        else:
            print("yisol returned no file:", result)
    except Exception as e:
        print("yisol FAILED:", e)
        import traceback
        traceback.print_exc()

    print()
    print("Done. Conclusion: frogleo/Kolors fail in standalone too (Space-side). Use yisol/IDM-VTON if available.")

if __name__ == "__main__":
    main()
