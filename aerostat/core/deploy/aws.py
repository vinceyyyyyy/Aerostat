import os
import subprocess
import tempfile
from pathlib import Path

from aerostat.core.deploy.common import render_html

from aerostat.core.utils import (
    get_module_version,
)


def deploy_to_aws(
    project_name: str,
    model_path: str,
    input_columns: list[str],
    python_dependencies: list[str],
    system_dependencies: list[str],
) -> None:
    """bundle a model with input column list"""

    # create a tmp directory for building aws lambda layer
    with tempfile.TemporaryDirectory() as tmp_dir:
        # render HTML template and save to tmp directory
        render_html(
            project_name=project_name,
            input_columns=input_columns,
            python_dependencies=python_dependencies,
            save_to=Path(tmp_dir) / "index.html",
        )

        # install python dependencies into tmp directory for building aws lambda layer
        python_dep_dir = (
            Path(tmp_dir) / "python" / "lib" / "python3.10" / "site-packages"
        )
        os.mkdir(python_dep_dir)
        os.system(f"pip install {' '.join(python_dependencies)} -t {python_dep_dir}")

        # deploy aws lambda and layer with cdk
        subprocess.run(
            [
                "cdk",
                "deploy",
                "--app",
                f"python {Path(__file__).parent}/cdk.py",
                "--context",
                f"layer_path={tmp_dir}",
                "--context",
                f"project_name={project_name}",
                "--context",
                f"input_columns={input_columns}",
            ]
        )


if __name__ == "__main__":
    print(get_module_version())
