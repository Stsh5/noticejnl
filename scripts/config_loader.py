"""
設定ファイル読み込みモジュール
config.json から検索条件・フィルタリング条件・Slack設定を読み込む
環境変数を使って動的に設定値を変更可能
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()


def _replace_env_variables(obj):
    """
    オブジェクト内の環境変数参照 (${VAR_NAME}) を実際の値に置換
    
    Args:
        obj: 文字列、リスト、辞書など任意のオブジェクト
    
    Returns:
        置換後のオブジェクト
    
    Raises:
        ValueError: 環境変数が見つからない場合
    """
    if isinstance(obj, str):
        # 文字列の場合、${VAR_NAME} パターンを置換
        if obj.startswith("${") and obj.endswith("}"):
            env_var_name = obj[2:-1]  # ${...} から ... を抽出
            env_value = os.getenv(env_var_name)
            
            if env_value is None:
                raise ValueError(f"Environment variable '{env_var_name}' not set")
            
            # JSON形式の場合はパース（例: ["keyword1", "keyword2"]）
            if env_value.strip().startswith("["):
                try:
                    return json.loads(env_value)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse JSON in environment variable '{env_var_name}': {env_value}")
            
            return env_value
        return obj
    
    elif isinstance(obj, dict):
        # 辞書の場合、各値に対して再帰的に置換
        return {key: _replace_env_variables(value) for key, value in obj.items()}
    
    elif isinstance(obj, list):
        # リストの場合、各要素に対して再帰的に置換
        return [_replace_env_variables(item) for item in obj]
    
    return obj


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
        ValueError: JSON解析エラー、必須設定がない場合、または環境変数が見つからない場合
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
    
    # 環境変数を置換
    config = _replace_env_variables(config)
    
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
