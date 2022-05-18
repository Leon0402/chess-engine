"""
Docs
"""
from pathlib import Path

from traitlets.config import Config
from nbconvert.exporters import PythonExporter


class JupyterLoader():
    """
    Docs
    """
    def __init__(self, output_directory="converted_notebooks"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

        config = Config()
        config.TagRemovePreprocessor.remove_cell_tags = ("no-python-export", )
        self.exporter = PythonExporter(config=config)

        self.exporter.exclude_markdown = True
        self.exporter.exclude_output = True
        self.exporter.exclude_output_prompt = True
        self.exporter.exclude_input_prompt = True

    def load(self, file: Path):
        """
        Docs
        """
        output, _ = self.exporter.from_file(file)

        python_file_path = self.output_directory / file.with_suffix(".py").name
        with open(python_file_path, "w", encoding="utf-8") as python_file:
            python_file.write(output)

    def load_all(self, directory: Path = Path(".")):
        """
        Docs
        """
        for file in directory.iterdir():
            if file.suffix == ".ipynb":
                self.load(file)
