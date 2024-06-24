import json
import os

from aws_lambda_powertools.utilities.typing import LambdaContext


def router(event: dict, context: LambdaContext) -> dict:
    """Router as lambda handler.
    Built router into lambda function and remove the needs for API Gateway to reduce system complexity.

    If no query param, return info HTML page, which include download link for the Excel template.
    If query param action=get_excel, return the Excel template.
    If query param action=predict, return the prediction result, along with all columns that are not specified in input_cols.

    :param event: API Gateway Lambda Proxy Input Format: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    :param context: Lambda Context runtime methods and attributes: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    :return: API Gateway Lambda Proxy Output Format: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    input_columns = eval(os.getenv("INPUT_COLUMNS"))
    model_path = f"{os.getenv('FUNCTION_DIR')}/model.pkl"
    api_endpoint = f"https://{event['headers']['host']}"

    if query_params := event.get("queryStringParameters"):
        if action := query_params.get("action"):
            if action == "get_excel":
                from excel import serve_excel

                # template_base.xlsm is mounted as part of lambda layer, and must be rendered in run time to include the api_endpoint
                return serve_excel(
                    excel_template_path="/opt/template_base.xlsm",
                    column_names=input_columns,
                    api_endpoint=api_endpoint,
                )
            if action == "predict":
                from predict import predict

                # request_body as {column_1: [value1, value2, ...], column_2: [value1, value2, ...], ...}
                return predict(
                    model_path=model_path,
                    data=json.loads(event["body"]),
                    input_columns=input_columns,
                )

    # no query param, return info page
    # index.html is rendered in build time, and mounted as part of lambda layer
    with open("/opt/index.html", "r") as f:
        html = f.read()
    return {
        "statusCode": 200,
        "body": html,
        "headers": {"Content-Type": "text/html"},
    }
