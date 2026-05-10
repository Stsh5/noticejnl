"""
Slack 通知モジュール
arXiv論文情報を Slack に通知する機能を提供
"""
import requests
from datetime import datetime


def format_slack_message(papers):
    """
    論文リストを Slack Block Kit メッセージにフォーマット
    
    Args:
        papers (list): 論文情報の辞書リスト
        
    Returns:
        dict: Slack Block Kit メッセージペイロード
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {...}
                },
                ...
            ]
        }
    """
    blocks = []
    
    # ヘッダーセクション
    header_text = f"📚 *{len(papers)} papers found*" if papers else "📚 *No papers found*"
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": header_text,
            "emoji": True
        }
    })
    
    # 各論文の情報
    for paper in papers:
        # タイトルと著者
        title = paper.get('title', 'Unknown title')
        authors = paper.get('authors', [])
        author_str = ', '.join(authors) if authors else 'Unknown author'
        url = paper.get('url', '#')
        published_date = paper.get('published_date', 'Unknown date')
        abstract = paper.get('abstract', 'No abstract available')
        
        # タイトル（リンク付き）
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{url}|*{title}*>"
            }
        })
        
        # 著者
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"👤 {author_str}"
                }
            ]
        })
        
        # 日時
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 {published_date}"
                }
            ]
        })
        
        # アブストラクト（最初の200文字）
        abstract_short = abstract[:200] + "..." if len(abstract) > 200 else abstract
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"_{abstract_short}_"
            }
        })
        
        # セパレータ
        blocks.append({
            "type": "divider"
        })
    
    # タイムスタンプ
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Updated: {current_time}"
            }
        ]
    })
    
    return {"blocks": blocks}


def send_slack_notification(papers, webhook_url):
    """
    Slack webhook を使用して通知を送信
    
    Args:
        papers (list): 論文情報の辞書リスト
        webhook_url (str): Slack Incoming Webhook URL
        
    Returns:
        bool: 送信成功時 True、失敗時は例外を発生
        
    Raises:
        ValueError: webhook_url が空の場合
        Exception: 送信失敗時
    """
    if not webhook_url:
        raise ValueError("webhook_url is required")
    
    # 空リストの場合は送信しない
    if not papers:
        return False
    
    message = format_slack_message(papers)
    
    try:
        response = requests.post(webhook_url, json=message)
        
        if response.status_code == 200:
            return True
        else:
            raise Exception(f"Slack webhook failed with status code {response.status_code}: {response.text}")
    
    except requests.RequestException as e:
        raise Exception(f"Failed to send Slack notification: {e}")
