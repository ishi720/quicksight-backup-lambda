# 概要

QuickSightの分析とデータセットの設定をLambdaでバックアップする

# Badge

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/02c0baa5c6204b7b8abe87dd7a01808c)](https://app.codacy.com/gh/ishi720/quicksight-backup-lambda/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# システム構成図

![quicksight-backup-lambda](https://github.com/user-attachments/assets/2361b46e-ab8c-49d9-aa0f-7732bd9c1718)


# 初期設定

## アクセスキーの設定

- AWS IAMのユーザーからアクセスキーを発行する
- `Settings` > `Secrets and variables` > `Actions` > `New repository secret`で下記を設定を行う
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`

## lambdaに関数を作成する

- `quicksight-backup`という名前で関数を作成する

# デプロイ

- Githubのmainブランチにpushする
