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

def lambda_handler(event, context):
    # データソース（Data Source）のバックアップ
    logger.info("- データソースのバックアップ開始 -")
    datasources = quicksight.list_data_sources(AwsAccountId=ACCOUNT_ID)
    for datasource in datasources.get("DataSources", []):
        datasource_id = datasource["DataSourceId"]
        datasource_name = datasource.get("Name", "Unknown")
        try:
            response = quicksight.describe_data_source(
                AwsAccountId=ACCOUNT_ID,
                DataSourceId=datasource_id
            )
            upload_to_s3("datasource", datasource_id, response, datasource_name)
        except quicksight.exceptions.InvalidParameterValueException as e:
            logger.warning(f"[Skip] 「{datasource_name}({datasource_id})」 - {e}")
        except Exception as e:
            logger.error(f"[Error] 「{datasource_name}({datasource_id})」 - {e}")
    logger.info("- データソースのバックアップ終了 -")


    # データセット(DataSet)のバックアップ
    logger.info("- データセットのバックアップ開始 -")
    datasets = quicksight.list_data_sets(AwsAccountId=ACCOUNT_ID)
    for dataset in datasets.get("DataSetSummaries", []):
        dataset_id = dataset["DataSetId"]
        dataset_name = dataset.get("Name", "Unknown")
        try:
            response = quicksight.describe_data_set(
                AwsAccountId=ACCOUNT_ID,
                DataSetId=dataset_id
            )
            upload_to_s3("dataset", dataset_id, response, dataset_name)
        except quicksight.exceptions.InvalidParameterValueException as e:
            logger.warning(f"[Skip] 「{dataset_name}({dataset_id})」 - {e}")
        except Exception as e:
            logger.error(f"[Error] 「{dataset_name}({dataset_id})」 - {e}")
    logger.info("- データセットのバックアップ終了 -")

    # 分析(Analysis)のバックアップ
    logger.info("- 分析のバックアップ開始 -")
    analyses = quicksight.list_analyses(AwsAccountId=ACCOUNT_ID)
    for analysis in analyses.get("AnalysisSummaryList", []):
        analysis_id = analysis["AnalysisId"]
        analysis_name = analysis.get("Name", "Unknown")
        try:
            response = quicksight.describe_analysis(
                AwsAccountId=ACCOUNT_ID,
                AnalysisId=analysis_id
            )
            upload_to_s3("analysis", analysis_id, response, analysis_name)
        except quicksight.exceptions.InvalidParameterValueException as e:
            logger.warning(f"[Skip] 「{analysis_name}({analysis_id})」 - {e}")
        except Exception as e:
            logger.error(f"[Error] 「{analysis_name}({analysis_id})」 - {e}")
    logger.info("- 分析のバックアップ終了 -")

    # ダッシュボード(Dashboard)のバックアップ
    logger.info("- ダッシュボードのバックアップ開始 -")
    dashboards = quicksight.list_dashboards(AwsAccountId=ACCOUNT_ID)
    for dashboard in dashboards.get("DashboardSummaryList", []):
        dashboard_id = dashboard["DashboardId"]
        dashboard_name = dashboard.get("Name", "Unknown")
        try:
            response = quicksight.describe_dashboard(
                AwsAccountId=ACCOUNT_ID,
                DashboardId=dashboard_id
            )
            upload_to_s3("dashboard", dashboard_id, response, dashboard_name)
        except quicksight.exceptions.InvalidParameterValueException as e:
            logger.warning(f"[Skip] 「{dashboard_name}({dashboard_id})」 - {e}")
        except Exception as e:
            logger.error(f"[Error] 「{dashboard_name}({dashboard_id})」 - {e}")
    logger.info("- ダッシュボードのバックアップ終了 -")

    return {
        "statusCode": 200,
        "body": json.dumps("QuickSight backup completed.")
    }