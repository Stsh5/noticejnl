# arXiv論文スクレイピング & Slack自動通知システム

## プロジェクト概要

このプロジェクトは，arXivから過去3日以内に投稿された論文をスクレイピングし、特定キーワード（例えば，**"silica clathrate"**, **"clathrasil"**）でフィルタリングしたうえで、Slack経由で自動通知するシステムです。

Windows Task Schedulerにより毎日8:00に自動実行されます。

## 仕様

### 主要機能

#### 1. arXiv スクレイピング機能 (`arxiv_scraper.py`)
- arXiv Feed API（RSS）から論文情報を取得
- 過去3日以内（72時間以内）に投稿された論文をフィルタリング
- 必須情報の抽出：
  - 論文ID
  - タイトル
  - 著者リスト
  - 公開日時
  - arXiv URL
  - アブストラクト
  
#### 2. キーワードマッチング機能 (`arxiv_scraper.py`)
- 対象キーワード：
  - `silica clathrate`
  - `clathrasil`
- マッチング対象フィールド：
  - タイトル
  - アブストラクト
- マッチング方式：大文字小文字区別なし

#### 3. Slack通知機能 (`slack_notifier.py`)
- Slack Incoming Webhook経由で通知
- 通知フォーマット：
  - ヘッダー：マッチ論文数
  - 各論文の詳細（タイトル、著者、URL等）
  - タイムスタンプ

#### 4. スケジューリング機能
- Windows Task Scheduler登録用スクリプト (`setup_scheduler.ps1`)
- 実行時刻：毎日8:00 AM
- ログ出力：実行結果をファイルに記録

### 設定

#### 環境変数
- `SLACK_WEBHOOK_URL`：Slack Incoming Webhook URL（必須）

#### 設定ファイル (`config.json`)
```json
{
  "keywords": ["silica clathrate", "clathrasil"],
  "days_back": 3,
  "slack_webhook_url": "${SLACK_WEBHOOK_URL}",
  "log_dir": "logs"
}
```

### エラーハンドリング
- arXiv API 接続失敗時：エラーログ出力、Slack通知
- Webhook URL 未設定時：明確なエラーメッセージ
- ネットワークエラー時：リトライロジック（3回まで）

### ログ出力
- ファイル保存先：`logs/`ディレクトリ
- ログファイル名：`arxiv_[YYYY-MM-DD].log`
- ログレベル：DEBUG, INFO, WARNING, ERROR

## ディレクトリ構造

```
dev-noticejnl/
├── README.md                      # このファイル
├── LOGGING.md                     # 修正・変更ログ
├── scripts/
│   ├── __init__.py
│   ├── main.py                    # エントリーポイント
│   ├── arxiv_scraper.py           # arXivスクレイピング
│   ├── slack_notifier.py          # Slack通知
│   ├── config.json                # 設定ファイル
│   └── setup_scheduler.ps1        # Task Scheduler設定
├── tests/
│   ├── __init__.py
│   ├── test_arxiv_scraper.py      # スクレイピング機能テスト
│   ├── test_slack_notifier.py     # Slack通知テスト
│   └── test_main.py               # 統合テスト
├── logs/                          # ログ出力ディレクトリ（実行時生成）
└── requirements.txt               # Python依存ライブラリ
```

## 技術スタック

- **言語：** Python 3.8+
- **主要ライブラリ：**
  - `feedparser`：RSS/Atom解析
  - `requests`：HTTP通信
  - `pytest`：ユニットテスト
  - `pytest-mock`：モッキング
  - `python-dateutil`：日時処理

## 開発フロー

1. **テストを先に記述** (TDD)
2. **テストに基づいて実装**
3. **全テスト合格を確認**
4. 変更内容を `LOGGING.md` に記録

## 使用方法

### セットアップ

#### 1. リポジトリをクローン
```bash
git clone https://github.com/Stsh5/noticejnl.git
cd noticejnl
```

#### 2. Python依存ライブラリをインストール
```bash
pip install -r requirements.txt
```

#### 3. 環境変数を設定

**方法A: .env ファイルを使用（推奨）**

プロジェクトルートに `.env` ファイルを作成してください：
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

ファイル作成方法：
- Windows (PowerShell):
  ```powershell
  echo 'SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' > .env
  ```
- Windows (コマンドプロンプト):
  ```cmd
  echo SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL > .env
  ```
- Linux/Mac:
  ```bash
  echo 'SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' > .env
  ```

**方法B: 環境変数をシェルで直接設定**

- Windows (PowerShell):
  ```powershell
  $env:SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
  python scripts/main.py
  ```

**Slack Webhook URL の取得方法:**
1. Slack App を開く
2. 通知を送るチャンネルを選択
3. 「Incoming Webhooks」を設定
4. 生成された Webhook URL をコピー

### テスト実行

```bash
# 全テストを実行
pytest tests/ -v

# 個別テスト実行
pytest tests/test_collecting.py -v
pytest tests/test_config_loader.py -v
pytest tests/test_filtering.py -v
pytest tests/test_slack_notifier.py -v
pytest tests/test_main.py -v

# 簡易検証スクリプト
python verify_filtering_tests.py
python verify_tests.py
```

### 手動実行

```bash
# アプリケーションを実行
python scripts/main.py
```

実行結果例：
```
2026-05-11 08:04:22,074 - INFO - Starting arXiv paper notification workflow...
2026-05-11 08:04:22,074 - INFO - Loading configuration...
2026-05-11 08:04:22,092 - INFO - Search query: silica clathrate OR clathrasil, Max results: 100, Days back: 3
2026-05-11 08:04:22,096 - INFO - Fetching papers from arXiv...
2026-05-11 08:04:23,955 - INFO - Fetched 100 papers
2026-05-11 08:04:23,957 - INFO - Filtering papers by date and keywords...
2026-05-11 08:04:23,967 - INFO - Filtered to 0 papers
2026-05-11 08:04:23,969 - INFO - Workflow completed successfully
```

### Task Scheduler 設定（Windows自動実行）

毎日8:00に自動実行させるには：

```powershell
cd scripts
.\setup_scheduler.ps1
```

このスクリプトが以下を設定します：
- 実行時刻: 毎日 8:00 AM
- 実行コマンド: `python scripts/main.py`
- ログ出力: 実行結果をファイルに記録


## API仕様

### arXiv Feed API
- エンドポイント：`https://export.arxiv.org/api/query`
- パラメータ例：
  ```
  search_query=cat:cond-mat&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending
  ```

### Slack Incoming Webhook
- POSTリクエストで JSON ペイロードを送信
- メッセージフォーマット：Block Kit対応

## トラブルシューティング

| 問題 | 原因 | 解決策 |
|------|------|--------|
| Slack通知されない | Webhook URL未設定 | `SLACK_WEBHOOK_URL`環境変数を確認 |
| arXivに接続できない | ネットワークエラー | インターネット接続確認、リトライロジック作動 |
| Task Scheduler実行されない | スケジューラ設定未完了 | `setup_scheduler.ps1` を再実行 |

## ライセンス

MIT License

## 作成者

- GitHub Copilot CLI

---

**最終更新：** 2026-05-06
