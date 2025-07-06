import boto3
import json
import datetime
import os

# S3設定（環境変数から取得）
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_PREFIX = os.environ.get("S3_PREFIX", "quicksight_backup/")
REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID")

quicksight = boto3.client("quicksight", region_name=REGION)
s3 = boto3.client("s3")

def lambda_handler(event, context):
    # データセット(DataSet)のバックアップ
    datasets = quicksight.list_data_sets(AwsAccountId=ACCOUNT_ID)
    for dataset in datasets.get("DataSetSummaries", []):
        dataset_id = dataset["DataSetId"]
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
        except quicksight.exceptions.InvalidParameterValueException as e:
            print(f"[Skip] 非対応データセット: {dataset_id} - {e}")
        except Exception as e:
            print(f"[Error] データセット取得失敗: {dataset_id} - {e}")

    # 分析(Analysis)のバックアップ
    analyses = quicksight.list_analyses(AwsAccountId=ACCOUNT_ID)
    for analysis in analyses.get("AnalysisSummaryList", []):
        analysis_id = analysis["AnalysisId"]
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
        except quicksight.exceptions.InvalidParameterValueException as e:
            print(f"[Skip] 非対応分析: {analysis_id} - {e}")
        except Exception as e:
            print(f"[Error] 分析取得失敗: {analysis_id} - {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("QuickSight backup completed.")
    }