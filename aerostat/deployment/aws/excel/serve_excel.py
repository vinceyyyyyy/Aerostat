import importlib.resources
from importlib.abc import Traversable

from .template import create_template


def serve_excel(
    excel_template_path: str,
    column_names: list[str],
    api_endpoint: str,
    table_name: str = "INPUT_TABLE",
):
    return create_template(
        excel_template_path=excel_template_path,
        column_names=column_names,
        api_endpoint=api_endpoint,
        table_name=table_name,
    )


def find_static_resource_path(module: str, filename: str = "") -> Traversable:
    try:
        return importlib.resources.files(module).joinpath(filename)
    except Exception:
        raise ValueError(f"Cannot open {filename}")
