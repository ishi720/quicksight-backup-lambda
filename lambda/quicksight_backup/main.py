import boto3
import json
import os
import logging

# ロガー設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# S3設定（環境変数から取得）
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_PREFIX = os.environ.get("S3_PREFIX", "quicksight_backup/")
REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID")

quicksight = boto3.client("quicksight", region_name=REGION)
s3 = boto3.client("s3")

def upload_to_s3(category, item_id, content, name):
    """
    指定されたQuickSightリソースの情報をS3バケットにJSON形式でアップロードする

    Parameters:
        category (str): リソースのカテゴリ（例: "datasource", "dataset", "analysis", "dashboard"）
        item_id (str): リソースの一意なID
        content (dict): アップロード対象のJSONデータ（describe_xxxのレスポンス）
        name (str): 表示名

    Raises:
        boto3.exceptions.Boto3Error: S3アップロードに失敗した場合にログにエラーを記録する
    """
    key = f"{S3_PREFIX}{category}/{category}_{item_id}.json"
    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(content, indent=2, default=str),
            ContentType="application/json"
        )
        logger.info(f"[Success] 「{name}({item_id})」 > {key}")
    except Exception as e:
        logger.error(f"[Error] S3 upload failed for 「{name}({item_id})」 - {e}")

def backup_quicksight_resource(category, list_func_name, list_key, describe_func_name, id_key, name_key="Name"):
    """
    QuickSightリソースの一覧取得とS3バックアップを行う

    Parameters:
        category (str): リソースの種類（例: 'dataset'）
        list_func_name (str): 一覧取得API名（例: 'list_data_sets'）
        list_key (str): 一覧レスポンスのキー（例: 'DataSetSummaries'）
        describe_func_name (str): 詳細取得API名（例: 'describe_data_set'）
        id_key (str): IDフィールドのキー（例: 'DataSetId'）
        name_key (str): 名前フィールドのキー（例: 'Name'）
    """
    logger.info(f"- {category.capitalize()} のバックアップ開始 -")

    try:
        list_func = getattr(quicksight, list_func_name)
        describe_func = getattr(quicksight, describe_func_name)
    except AttributeError as e:
        logger.error(f"[Error] API関数の取得に失敗しました: {e}")
        return

    try:
        resources = list_func(AwsAccountId=ACCOUNT_ID).get(list_key, [])
    except Exception as e:
        logger.error(f"[Error] {category.capitalize()}一覧の取得に失敗しました: {e}")
        return

    for item in resources:
        item_id = item.get(id_key)
        item_name = item.get(name_key, "Unknown")
        try:
            response = describe_func(AwsAccountId=ACCOUNT_ID, **{id_key: item_id})
            upload_to_s3(category, item_id, response, item_name)
        except quicksight.exceptions.InvalidParameterValueException as e:
            logger.warning(f"[Skip] 「{item_name}({item_id})」 - {e}")
        except Exception as e:
            logger.error(f"[Error] 「{item_name}({item_id})」 - {e}")
    logger.info(f"- {category.capitalize()} のバックアップ終了 -")


def lambda_handler(event, context):
    backup_quicksight_resource(
        category="datasource",
        list_func_name="list_data_sources",
        list_key="DataSources",
        describe_func_name="describe_data_source",
        id_key="DataSourceId"
    )
    backup_quicksight_resource(
        category="dataset",
        list_func_name="list_data_sets",
        list_key="DataSetSummaries",
        describe_func_name="describe_data_set",
        id_key="DataSetId"
    )
    backup_quicksight_resource(
        category="analysis",
        list_func_name="list_analyses",
        list_key="AnalysisSummaryList",
        describe_func_name="describe_analysis",
        id_key="AnalysisId"
    )
    backup_quicksight_resource(
        category="dashboard",
        list_func_name="list_dashboards",
        list_key="DashboardSummaryList",
        describe_func_name="describe_dashboard",
        id_key="DashboardId"
    )

    return {
        "statusCode": 200,
        "body": json.dumps("QuickSight backup completed.")
    }