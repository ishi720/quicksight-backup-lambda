import boto3
import json
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
    print(f"- データセットのバックアップ開始 -")
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
            print(f"[Success] 「{dataset_name}({dataset_id})」 > {key}")
        except quicksight.exceptions.InvalidParameterValueException as e:
            print(f"[Skip] 「{dataset_name}({dataset_id})」 - {e}")
        except Exception as e:
            print(f"[Error] 「{dataset_name}({dataset_id})」 - {e}")
    print(f"- データセットのバックアップ終了 -")

    # 分析(Analysis)のバックアップ
    print(f"- 分析のバックアップ開始 -")
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
            print(f"[Success] 「{analysis_name}({analysis_id})」 > {key}")
        except quicksight.exceptions.InvalidParameterValueException as e:
            print(f"[Skip] 「{analysis_name}({analysis_id})」 - {e}")
        except Exception as e:
            print(f"[Error] 「{analysis_name}({analysis_id})」 - {e}")
    print(f"- 分析のバックアップ終了 -")

    return {
        "statusCode": 200,
        "body": json.dumps("QuickSight backup completed.")
    }