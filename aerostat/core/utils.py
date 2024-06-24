import os
import tempfile
from datetime import datetime
from importlib import import_module, resources
from importlib.abc import Traversable

import jinja2


def create_tmp_dir():
    """Create a system tmp directory for temporary files"""
    return tempfile.TemporaryDirectory()


def find_static_resource_path(module: str, filename: str = "") -> Traversable:
    """Load Vega spec template from file"""
    try:
        return resources.files(module).joinpath(filename)
    except Exception:
        raise ValueError(f"Cannot open {filename}")


def sanitize_service_name(service_name: str):
    """Sanitize service name"""
    return service_name.lower().replace(" ", "-").replace("_", "-")


def get_system_dependencies(python_dependencies: list[str]) -> list[str]:
    """get system dependencies from certain known ML libraries"""
    system_dependencies = []
    if "lightgbm" in [s.lower() for s in python_dependencies]:
        system_dependencies.append("libgomp1")
    return system_dependencies


def get_module_version() -> str:
    """Get module version"""
    return import_module("aerostat").__version__


def render_html(
    project_name: str,
    input_columns: list[str],
    python_dependencies: list[str],
    save_to: str = None,
):
    environment = jinja2.Environment()
    template = environment.from_string(
        find_static_resource_path("aerostat.static", "index.jinja").read_text(
            encoding="utf-8"
        )
    )
    result = template.render(
        project_name=project_name,
        build_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        input_columns=input_columns,
        python_dependencies=python_dependencies,
        aerostat_version=get_module_version(),
    )

    if save_to:
        os.makedirs(os.path.dirname(save_to), exist_ok=True)
        with open(save_to, "w") as f:
            f.write(result)

    return result
