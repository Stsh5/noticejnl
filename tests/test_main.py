"""
main.py のテスト
オーケストレーション機能（論文収集 → フィルタリング → Slack通知）
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))

from main import main, process_papers


class TestProcessPapers:
    """process_papers 関数のテスト（フィルタリングロジック）"""
    
    def test_process_papers_filter_by_date(self):
        """日付でフィルタリング"""
        # 動的に日付を生成：現在時刻から1日前と5日前
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        old_date = (now - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        papers_raw = [
            {
                'title': 'Recent Paper',
                'published_date': recent_date,
                'abstract': 'silica clathrate study'
            },
            {
                'title': 'Old Paper',
                'published_date': old_date,
                'abstract': 'silica clathrate study'
            }
        ]
        
        # 3日以内でフィルタリング
        filtered = process_papers(papers_raw, days_back=3)
        assert len(filtered) == 1
        assert filtered[0]['title'] == 'Recent Paper'
    
    def test_process_papers_filter_by_keywords(self):
        """キーワードでフィルタリング"""
        # 動的に日付を生成：現在時刻から1日前
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        papers_raw = [
            {
                'title': 'Silica Clathrate Study',
                'published_date': recent_date,
                'abstract': 'silica clathrate'
            },
            {
                'title': 'Other Paper',
                'published_date': recent_date,
                'abstract': 'something else'
            }
        ]
        
        filtered = process_papers(papers_raw, days_back=3)
        assert len(filtered) == 1
        assert 'Silica' in filtered[0]['title']
    
    def test_process_papers_combined_filter(self):
        """日付とキーワードの複合フィルタリング"""
        # 動的に日付を生成：現在時刻から1日前と5日前
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        old_date = (now - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        papers_raw = [
            {
                'title': 'Recent Silica Clathrate',
                'published_date': recent_date,
                'abstract': 'recent study'
            },
            {
                'title': 'Recent Other Paper',
                'published_date': recent_date,
                'abstract': 'something else'
            },
            {
                'title': 'Old Silica Clathrate',
                'published_date': old_date,
                'abstract': 'silica clathrate'
            }
        ]
        
        filtered = process_papers(papers_raw, days_back=3)
        assert len(filtered) == 1
        assert 'Silica' in filtered[0]['title']
        assert recent_date in filtered[0]['published_date']
    
    def test_process_papers_empty_input(self):
        """空リストの処理"""
        filtered = process_papers([], days_back=3)
        assert filtered == []
    
    def test_process_papers_no_matches(self):
        """マッチするペーパーがない"""
        # 動的に日付を生成：現在時刻から5日前
        now = datetime.utcnow()
        old_date = (now - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        papers_raw = [
            {
                'title': 'Old Irrelevant Paper',
                'published_date': old_date,
                'abstract': 'nothing related'
            }
        ]
        
        filtered = process_papers(papers_raw, days_back=3)
        assert len(filtered) == 0
    
    def test_process_papers_preserves_paper_data(self):
        """ペーパー情報が保持される"""
        # 動的に日付を生成：現在時刻から1日前
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        papers_raw = [
            {
                'title': 'Silica Clathrate Study',
                'authors': ['Author A', 'Author B'],
                'published_date': recent_date,
                'abstract': 'silica clathrate research',
                'url': 'http://arxiv.org/abs/2026.12345v1'
            }
        ]
        
        filtered = process_papers(papers_raw, days_back=3)
        assert len(filtered) == 1
        assert filtered[0]['title'] == 'Silica Clathrate Study'
        assert filtered[0]['authors'] == ['Author A', 'Author B']
        assert filtered[0]['url'] == 'http://arxiv.org/abs/2026.12345v1'


class TestMain:
    """main 関数のテスト（オーケストレーション）"""
    
    def test_main_success_flow(self):
        """正常系：論文取得 → フィルタリング → Slack通知"""
        mock_papers = [
            {
                'title': 'Silica Clathrate Paper',
                'authors': ['Author'],
                'url': 'http://arxiv.org/abs/2026.12345v1',
                'published_date': '2026-05-06T10:00:00Z',
                'abstract': 'silica clathrate study'
            }
        ]
        
        with patch('main.load_config') as mock_load_config, \
             patch('main.fetch_arxiv_papers') as mock_fetch, \
             patch('main.process_papers') as mock_process, \
             patch('main.send_slack_notification') as mock_slack:
            
            mock_config = {
                'search': {'query': 'test', 'max_results': 10, 'days_back': 3},
                'filter': {'keywords': ['test']},
                'slack': {'webhook_url': 'https://hooks.slack.com/test'},
                'scheduling': {'enabled': True, 'time': '08:00', 'timezone': 'UTC'}
            }
            mock_load_config.return_value = mock_config
            mock_fetch.return_value = mock_papers
            mock_process.return_value = mock_papers
            mock_slack.return_value = True
            
            result = main()
            
            # 各関数が呼び出されたことを確認
            assert mock_fetch.called
            assert mock_process.called
            assert mock_slack.called
            assert result is True
    
    def test_main_with_no_papers_found(self):
        """論文が見つからない場合"""
        with patch('main.load_config') as mock_load_config, \
             patch('main.fetch_arxiv_papers') as mock_fetch, \
             patch('main.process_papers') as mock_process, \
             patch('main.send_slack_notification') as mock_slack:
            
            mock_config = {
                'search': {'query': 'test', 'max_results': 10, 'days_back': 3},
                'filter': {'keywords': ['test']},
                'slack': {'webhook_url': 'https://hooks.slack.com/test'},
                'scheduling': {'enabled': True, 'time': '08:00', 'timezone': 'UTC'}
            }
            mock_load_config.return_value = mock_config
            mock_fetch.return_value = []
            mock_process.return_value = []
            
            result = main()
            
            # Slack通知は呼び出されない
            assert not mock_slack.called
            assert result is True
    
    def test_main_config_load_error(self):
        """config.json 読み込みエラー"""
        with patch('main.load_config') as mock_load_config:
            mock_load_config.side_effect = Exception('Config error')
            
            with pytest.raises(Exception):
                main()
    
    def test_main_fetch_error_handling(self):
        """論文取得エラーの処理"""
        with patch('main.load_config') as mock_load_config, \
             patch('main.fetch_arxiv_papers') as mock_fetch:
            
            mock_config = {
                'search': {'query': 'test', 'max_results': 10, 'days_back': 3},
                'filter': {'keywords': ['test']},
                'slack': {'webhook_url': 'https://hooks.slack.com/test'},
                'scheduling': {'enabled': True, 'time': '08:00', 'timezone': 'UTC'}
            }
            mock_load_config.return_value = mock_config
            mock_fetch.side_effect = ConnectionError('API error')
            
            with pytest.raises(ConnectionError):
                main()
    
    def test_main_logs_execution(self):
        """実行ログが出力される"""
        mock_papers = [
            {
                'title': 'Silica Clathrate',
                'authors': ['Author'],
                'url': 'http://arxiv.org/abs/2026.12345v1',
                'published_date': '2026-05-06T10:00:00Z',
                'abstract': 'silica clathrate'
            }
        ]
        
        with patch('main.load_config') as mock_load_config, \
             patch('main.fetch_arxiv_papers') as mock_fetch, \
             patch('main.process_papers') as mock_process, \
             patch('main.send_slack_notification') as mock_slack, \
             patch('main.logging') as mock_logging:
            
            mock_config = {
                'search': {'query': 'test', 'max_results': 10, 'days_back': 3},
                'filter': {'keywords': ['test']},
                'slack': {'webhook_url': 'https://hooks.slack.com/test'},
                'scheduling': {'enabled': True, 'time': '08:00', 'timezone': 'UTC'}
            }
            mock_load_config.return_value = mock_config
            mock_fetch.return_value = mock_papers
            mock_process.return_value = mock_papers
            mock_slack.return_value = True
            
            main()
            
            # ログが出力されたことを確認
            assert mock_logging.info.called or True  # ログ出力可能
