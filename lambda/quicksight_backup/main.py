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
            key = f"{S3_PREFIX}datasource/datasource_{datasource_id}.json"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=json.dumps(response, indent=2, default=str),
                ContentType="application/json"
            )
            logger.info(f"[Success] 「{datasource_name}({datasource_id})」 > {key}")
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
            key = f"{S3_PREFIX}dataset/dataset_{dataset_id}.json"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=json.dumps(response, indent=2, default=str),
                ContentType="application/json"
            )
            logger.info(f"[Success] 「{dataset_name}({dataset_id})」 > {key}")
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
            key = f"{S3_PREFIX}analysis/analysis_{analysis_id}.json"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=json.dumps(response, indent=2, default=str),
                ContentType="application/json"
            )
            logger.info(f"[Success] 「{analysis_name}({analysis_id})」 > {key}")
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
            key = f"{S3_PREFIX}dashboard/dashboard_{dashboard_id}.json"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=json.dumps(response, indent=2, default=str),
                ContentType="application/json"
            )
            logger.info(f"[Success] 「{dashboard_name}({dashboard_id})」 > {key}")
        except quicksight.exceptions.InvalidParameterValueException as e:
            logger.warning(f"[Skip] 「{dashboard_name}({dashboard_id})」 - {e}")
        except Exception as e:
            logger.error(f"[Error] 「{dashboard_name}({dashboard_id})」 - {e}")
    logger.info("- ダッシュボードのバックアップ終了 -")

    return {
        "statusCode": 200,
        "body": json.dumps("QuickSight backup completed.")
    }