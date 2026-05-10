"""
設定ファイル読み込みモジュール
config.json から検索条件・フィルタリング条件・Slack設定を読み込む
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()


def load_config(config_path=None):
    """
    config.json を読み込む
    
    Args:
        config_path (str): config.json のパス。指定なしの場合は scripts/config.json を使用
    
    Returns:
        dict: 設定ファイルの内容
        {
            "search": {
                "query": "検索クエリ",
                "max_results": 最大件数,
                "days_back": 日数
            },
            "filter": {
                "keywords": ["キーワード1", "キーワード2"]
            },
            "slack": {
                "webhook_url": "webhook URL"
            },
            "scheduling": {
                "enabled": true/false,
                "time": "HH:MM",
                "timezone": "タイムゾーン"
            }
        }
    
    Raises:
        FileNotFoundError: config.json が見つからない場合
        ValueError: JSON解析エラーまたは必須設定がない場合
    """
    if config_path is None:
        # デフォルト: スクリプト同じディレクトリの config.json
        config_path = Path(__file__).parent / "config.json"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"config.json not found at {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse config.json: {e}")
    
    # 必須キーの確認
    required_keys = ["search", "filter", "slack", "scheduling"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key '{key}' in config.json")
    
    # 環境変数を置換 (${SLACK_WEBHOOK_URL} → 環境変数の値)
    webhook_url = config.get("slack", {}).get("webhook_url", "")
    if webhook_url.startswith("${") and webhook_url.endswith("}"):
        env_var_name = webhook_url[2:-1]  # ${...} から ... を抽出
        webhook_url = os.getenv(env_var_name, "")
        if not webhook_url:
            raise ValueError(f"Environment variable '{env_var_name}' not set")
        config["slack"]["webhook_url"] = webhook_url
    
    return config


def get_search_config(config):
    """
    config から search 設定を取得
    
    Args:
        config (dict): load_config() から取得した設定
    
    Returns:
        dict: {
            "query": "検索クエリ",
            "max_results": 最大件数,
            "days_back": 日数
        }
    """
    return config.get("search", {})


def get_filter_config(config):
    """
    config から filter 設定を取得
    
    Args:
        config (dict): load_config() から取得した設定
    
    Returns:
        dict: {"keywords": ["キーワード1", "キーワード2"]}
    """
    return config.get("filter", {})


def get_slack_config(config):
    """
    config から Slack 設定を取得
    
    Args:
        config (dict): load_config() から取得した設定
    
    Returns:
        dict: {"webhook_url": "Webhook URL"}
    """
    return config.get("slack", {})


def get_scheduling_config(config):
    """
    config から scheduling 設定を取得
    
    Args:
        config (dict): load_config() から取得した設定
    
    Returns:
        dict: {
            "enabled": true/false,
            "time": "HH:MM",
            "timezone": "タイムゾーン"
        }
    """
    return config.get("scheduling", {})
