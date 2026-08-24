from pathlib import Path

from app.modules.senate_reconstruction import write_outputs


if __name__ == "__main__":
    write_outputs(Path("data/oed/senate"))
