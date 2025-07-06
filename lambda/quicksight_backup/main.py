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
    # 分析(Analysis)のバックアップ
    analyses = quicksight.list_analyses(AwsAccountId=ACCOUNT_ID)
    for analysis in analyses.get("AnalysisSummaryList", []):
        analysis_id = analysis["AnalysisId"]
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

    return {
        "statusCode": 200,
        "body": json.dumps("QuickSight backup completed.")
    }