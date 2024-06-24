from pathlib import Path

from aws_cdk import aws_lambda as _lambda, App, RemovalPolicy, Stack


class AerostatStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        layer_path = self.node.try_get_context("layer_path")

        # create layer
        layer = _lambda.LayerVersion(
            self,
            "aerostat_layer",
            code=_lambda.Code.from_asset(layer_path),
            description="Dependencies for aerostat",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_10,
                _lambda.Runtime.PYTHON_3_11,
                _lambda.Runtime.PYTHON_3_12,
            ],
            removal_policy=RemovalPolicy.DESTROY,
        )

        # create lambda function
        function = _lambda.Function(
            self,
            "aerostat_function",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="index.handler",
            code=_lambda.Code.from_asset(
                Path(__file__).parent.parent / "deployment" / "aws"
            ),
            layers=[layer],
            environment={
                "INPUT_COLUMNS": self.node.try_get_context("input_columns"),
            },
        )


app = App()
project_name = app.node.try_get_context("project_name")
AerostatStack(app, project_name)
app.synth()
