"""
メイン実行モジュール
論文収集 → フィルタリング → Slack通知のオーケストレーション
"""
import logging
from collecting import fetch_arxiv_papers, is_recent, match_keywords
from slack_notifier import send_slack_notification
from config_loader import load_config, get_search_config, get_slack_config, get_scheduling_config

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_papers(papers_raw, days_back=3):
    """
    取得した論文をフィルタリング（日付 + キーワード）
    
    Args:
        papers_raw (list): fetch_arxiv_papers から取得した論文リスト（辞書形式）
        days_back (int): 何日以内の論文を対象とするか
    
    Returns:
        list: フィルタリング済み論文リスト
    """
    filtered = []
    
    for paper in papers_raw:
        # 辞書形式の論文オブジェクトを is_recent, match_keywords 用に変換
        class PaperEntry:
            def __init__(self, paper_dict):
                self.title = paper_dict.get('title', '')
                self.summary = paper_dict.get('abstract', '')
                self.published = paper_dict.get('published_date', '')
        
        entry = PaperEntry(paper)
        
        try:
            # 日付フィルタリング
            if not is_recent(entry, days=days_back):
                continue
            
            # キーワードフィルタリング
            if not match_keywords(entry):
                continue
            
            # 両方の条件を満たした論文を追加
            filtered.append(paper)
        except Exception as e:
            logger.warning(f"Error filtering paper {paper.get('title', 'Unknown')}: {e}")
            continue
    
    return filtered


def main():
    """
    メイン処理：論文収集 → フィルタリング → Slack通知
    
    Returns:
        bool: 処理成功時 True
        
    Raises:
        Exception: config.json 読み込みエラーなど
    """
    logger.info("Starting arXiv paper notification workflow...")
    
    try:
        # 1. 設定読み込み
        logger.info("Loading configuration...")
        config = load_config()
        
        search_config = get_search_config(config)
        slack_config = get_slack_config(config)
        scheduling_config = get_scheduling_config(config)
        
        query = search_config.get('query')
        max_results = search_config.get('max_results', 100)
        days_back = search_config.get('days_back', 3)
        webhook_url = slack_config.get('webhook_url')
        
        logger.info(f"Search query: {query}, Max results: {max_results}, Days back: {days_back}")
        
        # 2. arXiv から論文を取得
        logger.info("Fetching papers from arXiv...")
        papers_raw = fetch_arxiv_papers(query=query, max_results=max_results, config=config)
        logger.info(f"Fetched {len(papers_raw)} papers")
        
        # 3. フィルタリング
        logger.info("Filtering papers by date and keywords...")
        papers_filtered = process_papers(papers_raw, days_back=days_back)
        logger.info(f"Filtered to {len(papers_filtered)} papers")
        
        # 4. Slack通知
        if papers_filtered:
            logger.info(f"Sending {len(papers_filtered)} papers to Slack...")
            send_slack_notification(papers_filtered, webhook_url)
            logger.info("Slack notification sent successfully")
        else:
            logger.info("No papers matched the criteria, skipping Slack notification")
        
        logger.info("Workflow completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error in main workflow: {e}")
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
