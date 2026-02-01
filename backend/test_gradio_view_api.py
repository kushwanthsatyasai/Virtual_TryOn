"""
Print Gradio Space API (endpoints and parameters). Run with venv: python test_gradio_view_api.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    from gradio_client import Client

    for space in ["frogleo/AI-Clothes-Changer", "Kwai-Kolors/Kolors-Virtual-Try-On"]:
        print("=" * 60)
        print(space)
        print("=" * 60)
        try:
            client = Client(space)
            info = client.view_api(print_info=True, return_format="dict")
            if info:
                import json
                print("Named:", list(info.get("named_endpoints", {}).keys()))
                print("Unnamed (fn_index):", list(info.get("unnamed_endpoints", {}).keys()))
                for name, ep in info.get("unnamed_endpoints", {}).items():
                    print(f"  fn_index {name} params:", [p.get("label") for p in ep.get("parameters", [])])
        except Exception as e:
            print("Error:", e)
        print()

if __name__ == "__main__":
    main()
