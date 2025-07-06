AWS Lambdaにコードをデプロイする

# セットアップ

## アクセスキーの設定

- AWS IAMのユーザーからアクセスキーを発行する
- `Settings` > `Secrets and variables` > `Actions` > `New repository secret`で下記を設定を行う
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`

## lambdaに関数を作成する

`quicksight-backup`という名前で関数を作成する


## ランタイム設定

AWS上のlambda関数でハンドラを`quicksight_backup.main.lambda_handler`に変更する

## デプロイする

Githubのmainブランチにpushする
