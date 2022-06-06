"""
Docs
"""
from pathlib import Path

from traitlets.config import Config
from nbconvert.exporters import PythonExporter, MarkdownExporter


class JupyterLoader():
    """
    Docs
    """
    def __init__(self, python_output_directory="converted_notebooks", markdown_output_directory="converted_markdown"):
        self.python_output_directory = Path(python_output_directory)
        self.python_output_directory.mkdir(parents=True, exist_ok=True)

        config = Config()
        config.TagRemovePreprocessor.remove_cell_tags = ("no-python-export", )
        self.python_exporter = PythonExporter(config=config)

        self.python_exporter.exclude_markdown = True
        self.python_exporter.exclude_output = True
        self.python_exporter.exclude_output_prompt = True
        self.python_exporter.exclude_input_prompt = True

        self.markdown_output_directory = Path(markdown_output_directory)
        self.markdown_output_directory.mkdir(parents=True, exist_ok=True)

        self.markdown_exporter = MarkdownExporter()
        self.markdown_exporter.exclude_output = True

    def load_markdown(self, file: Path):
        """
        Docs
        """
        output, _ = self.markdown_exporter.from_file(file)

        markdown_file_path = self.markdown_output_directory / file.with_suffix(".md").name
        with open(markdown_file_path, "w", encoding="utf-8") as markdown_file:
            markdown_file.write(output)



    def load_python(self, file: Path):
        """
        Docs
        """
        output, _ = self.python_exporter.from_file(file)

        python_file_path = self.python_output_directory / file.with_suffix(".py").name
        with open(python_file_path, "w", encoding="utf-8") as python_file:
            python_file.write(output)

    def load_all(self, directory: Path = Path("."), export_python=True, export_markdown=True):
        """
        Docs
        """
        for file in directory.iterdir():
            if file.suffix == ".ipynb":
                if export_python:
                    self.load_python(file)
                if export_markdown:
                    self.load_markdown(file)
