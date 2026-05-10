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
```bash
pip install -r requirements.txt
```

### テスト実行
```bash
pytest tests/ -v
```

### 手動実行
```bash
python scripts/main.py
```

### Task Scheduler設定
```powershell
cd scripts
.\setup_scheduler.ps1
```

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
