from genericpath import exists
from traitlets.config import Config
from nbconvert.exporters import PythonExporter
from pathlib import Path


class JupyerLoader():
    """
    Docs
    """
    def __init__(self, directory="converted_notebooks"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

        c = Config()
        c.TagRemovePreprocessor.remove_cell_tags = ("no-python-export", )
        self.exporter = PythonExporter(config=c)

    def load(self, filename: str):
        """
        Docs
        """
        output, _ = self.exporter.from_filename(f"{filename}.ipynb")

        with open(self.directory / f"{filename}.py", "w") as f:
            f.write(output)