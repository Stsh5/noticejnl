"""
config_loader.py のテスト
config.json 読み込み機能をテスト
"""
import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))

from config_loader import (
    load_config,
    get_search_config,
    get_filter_config,
    get_slack_config,
    get_scheduling_config
)


class TestLoadConfig:
    """load_config 関数のテスト"""
    
    def test_load_config_default_path(self):
        """デフォルトパス (scripts/config.json) から設定を読み込む"""
        # デフォルト config.json は環境変数参照のため、環境変数がなくてもデフォルト値が使われる
        config = load_config()
        assert isinstance(config, dict)
        assert "search" in config
        assert "filter" in config
        assert "slack" in config
        assert "scheduling" in config
    
    def test_load_config_custom_path(self):
        """カスタムパスから設定を読み込む"""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            test_config = {
                "search": {"query": "test", "max_results": 10, "days_back": 1},
                "filter": {"keywords": ["test"]},
                "slack": {"webhook_url": "https://example.com"},
                "scheduling": {"enabled": False, "time": "09:00", "timezone": "UTC"}
            }
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            config = load_config(str(config_path))
            assert config == test_config
    
    def test_load_config_file_not_found(self):
        """config.json が見つからない場合は例外"""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.json")
    
    def test_load_config_invalid_json(self):
        """不正な JSON の場合は例外"""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            with open(config_path, 'w') as f:
                f.write("invalid json {")
            
            with pytest.raises(ValueError, match="Failed to parse config.json"):
                load_config(str(config_path))
    
    def test_load_config_missing_required_keys(self):
        """必須キーがない場合は例外"""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            incomplete_config = {
                "search": {"query": "test", "max_results": 10, "days_back": 1},
                "filter": {"keywords": ["test"]}
                # "slack" と "scheduling" がない
            }
            with open(config_path, 'w') as f:
                json.dump(incomplete_config, f)
            
            with pytest.raises(ValueError, match="Missing required key"):
                load_config(str(config_path))
    
    def test_load_config_environment_variable_substitution(self):
        """環境変数を置換する"""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            test_config = {
                "search": {"query": "test", "max_results": 10, "days_back": 1},
                "filter": {"keywords": ["test"]},
                "slack": {"webhook_url": "${TEST_WEBHOOK_URL}"},
                "scheduling": {"enabled": False, "time": "09:00", "timezone": "UTC"}
            }
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            with patch.dict(os.environ, {"TEST_WEBHOOK_URL": "https://hooks.slack.com/test"}):
                config = load_config(str(config_path))
                assert config["slack"]["webhook_url"] == "https://hooks.slack.com/test"
    
    def test_load_config_missing_environment_variable(self):
        """環境変数が設定されていない場合は例外"""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            test_config = {
                "search": {"query": "test", "max_results": 10, "days_back": 1},
                "filter": {"keywords": ["test"]},
                "slack": {"webhook_url": "${MISSING_WEBHOOK_URL}"},
                "scheduling": {"enabled": False, "time": "09:00", "timezone": "UTC"}
            }
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError, match="Environment variable"):
                    load_config(str(config_path))


class TestGetSearchConfig:
    """get_search_config 関数のテスト"""
    
    def test_get_search_config(self):
        """search 設定を取得"""
        config = {
            "search": {"query": "test query", "max_results": 50, "days_back": 2},
            "filter": {"keywords": ["test"]},
            "slack": {"webhook_url": "https://example.com"},
            "scheduling": {"enabled": True, "time": "08:00", "timezone": "UTC"}
        }
        search_config = get_search_config(config)
        assert search_config["query"] == "test query"
        assert search_config["max_results"] == 50
        assert search_config["days_back"] == 2


class TestGetFilterConfig:
    """get_filter_config 関数のテスト"""
    
    def test_get_filter_config(self):
        """filter 設定を取得"""
        config = {
            "search": {"query": "test", "max_results": 10, "days_back": 1},
            "filter": {"keywords": ["keyword1", "keyword2"]},
            "slack": {"webhook_url": "https://example.com"},
            "scheduling": {"enabled": False, "time": "09:00", "timezone": "UTC"}
        }
        filter_config = get_filter_config(config)
        assert filter_config["keywords"] == ["keyword1", "keyword2"]


class TestGetSlackConfig:
    """get_slack_config 関数のテスト"""
    
    def test_get_slack_config(self):
        """Slack 設定を取得"""
        config = {
            "search": {"query": "test", "max_results": 10, "days_back": 1},
            "filter": {"keywords": ["test"]},
            "slack": {"webhook_url": "https://hooks.slack.com/test"},
            "scheduling": {"enabled": False, "time": "09:00", "timezone": "UTC"}
        }
        slack_config = get_slack_config(config)
        assert slack_config["webhook_url"] == "https://hooks.slack.com/test"


class TestGetSchedulingConfig:
    """get_scheduling_config 関数のテスト"""
    
    def test_get_scheduling_config(self):
        """scheduling 設定を取得"""
        config = {
            "search": {"query": "test", "max_results": 10, "days_back": 1},
            "filter": {"keywords": ["test"]},
            "slack": {"webhook_url": "https://example.com"},
            "scheduling": {"enabled": True, "time": "08:00", "timezone": "Asia/Tokyo"}
        }
        scheduling_config = get_scheduling_config(config)
        assert scheduling_config["enabled"] is True
        assert scheduling_config["time"] == "08:00"
        assert scheduling_config["timezone"] == "Asia/Tokyo"
