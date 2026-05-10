"""
Slack 通知機能のテスト
slack_notifier.py の send_slack_notification() 関数をテスト
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))

from slack_notifier import send_slack_notification, format_slack_message


class TestFormatSlackMessage:
    """format_slack_message 関数のテスト"""
    
    def test_format_message_single_paper(self):
        """1件の論文をフォーマット"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author One', 'Author Two'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'This is a test abstract.'
        }]
        
        message = format_slack_message(papers)
        assert isinstance(message, dict)
        assert 'blocks' in message
        assert len(message['blocks']) > 0
    
    def test_format_message_multiple_papers(self):
        """複数件の論文をフォーマット"""
        papers = [
            {
                'title': 'Paper 1',
                'authors': ['Author A'],
                'url': 'http://arxiv.org/abs/2026.11111v1',
                'published_date': '2026-05-06T10:00:00Z',
                'abstract': 'Abstract 1'
            },
            {
                'title': 'Paper 2',
                'authors': ['Author B', 'Author C'],
                'url': 'http://arxiv.org/abs/2026.22222v1',
                'published_date': '2026-05-06T11:00:00Z',
                'abstract': 'Abstract 2'
            }
        ]
        
        message = format_slack_message(papers)
        assert isinstance(message, dict)
        assert 'blocks' in message
    
    def test_format_message_empty_papers(self):
        """空リストの場合"""
        papers = []
        message = format_slack_message(papers)
        assert isinstance(message, dict)
        assert 'blocks' in message
    
    def test_format_message_contains_title(self):
        """メッセージにタイトルが含まれる"""
        papers = [{
            'title': 'Silica Clathrate Study',
            'authors': ['John Doe'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Study of silica clathrate'
        }]
        
        message = format_slack_message(papers)
        message_text = json.dumps(message)
        assert 'Silica Clathrate Study' in message_text
    
    def test_format_message_contains_authors(self):
        """メッセージに著者が含まれる"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Alice Smith', 'Bob Johnson'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        
        message = format_slack_message(papers)
        message_text = json.dumps(message)
        assert 'Alice Smith' in message_text or 'Bob Johnson' in message_text
    
    def test_format_message_contains_url(self):
        """メッセージに arXiv URL が含まれる"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        
        message = format_slack_message(papers)
        message_text = json.dumps(message)
        assert 'http://arxiv.org/abs/2026.12345v1' in message_text
    
    def test_format_message_paper_count(self):
        """ヘッダーに論文数を表示"""
        papers = [
            {'title': f'Paper {i}', 'authors': ['A'], 'url': f'http://arxiv.org/{i}',
             'published_date': '2026-05-06T10:00:00Z', 'abstract': 'Test'}
            for i in range(3)
        ]
        
        message = format_slack_message(papers)
        message_text = json.dumps(message)
        # 3件の論文が見つかったことを表示
        assert '3' in message_text or 'papers' in message_text.lower()


class TestSendSlackNotification:
    """send_slack_notification 関数のテスト"""
    
    def test_send_notification_success(self):
        """Slack 通知送信成功"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        webhook_url = 'https://hooks.slack.com/services/T/B/XXXXX'
        
        with patch('slack_notifier.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            result = send_slack_notification(papers, webhook_url)
            assert result is True
            mock_post.assert_called_once()
    
    def test_send_notification_with_empty_papers(self):
        """空リストで通知送信（スキップすべき）"""
        papers = []
        webhook_url = 'https://hooks.slack.com/services/T/B/XXXXX'
        
        with patch('slack_notifier.requests.post') as mock_post:
            result = send_slack_notification(papers, webhook_url)
            # 空リストの場合は送信しない
            assert result is False
            mock_post.assert_not_called()
    
    def test_send_notification_network_error(self):
        """ネットワークエラー時"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        webhook_url = 'https://hooks.slack.com/services/T/B/XXXXX'
        
        with patch('slack_notifier.requests.post') as mock_post:
            mock_post.side_effect = Exception('Connection error')
            
            with pytest.raises(Exception):
                send_slack_notification(papers, webhook_url)
    
    def test_send_notification_invalid_webhook_url(self):
        """無効な webhook URL"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        
        with pytest.raises(ValueError, match='webhook_url'):
            send_slack_notification(papers, '')
    
    def test_send_notification_success_http_status(self):
        """HTTP ステータスコード 200 確認"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        webhook_url = 'https://hooks.slack.com/services/T/B/XXXXX'
        
        with patch('slack_notifier.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            result = send_slack_notification(papers, webhook_url)
            assert result is True
    
    def test_send_notification_failure_http_status(self):
        """HTTP エラーステータス"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        webhook_url = 'https://hooks.slack.com/services/T/B/XXXXX'
        
        with patch('slack_notifier.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception, match='failed'):
                send_slack_notification(papers, webhook_url)
    
    def test_send_notification_payload_format(self):
        """Slack ペイロード形式確認"""
        papers = [{
            'title': 'Test Paper',
            'authors': ['Author'],
            'url': 'http://arxiv.org/abs/2026.12345v1',
            'published_date': '2026-05-06T10:00:00Z',
            'abstract': 'Test'
        }]
        webhook_url = 'https://hooks.slack.com/services/T/B/XXXXX'
        
        with patch('slack_notifier.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            send_slack_notification(papers, webhook_url)
            
            # POST 呼び出しをチェック
            assert mock_post.called
            call_args = mock_post.call_args
            # json パラメータが渡されている
            assert 'json' in call_args.kwargs or len(call_args.args) > 1
