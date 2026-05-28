import logging
from app.infra.supabase_client import get_supabase
from app.infra.services.gmail_service import GmailService

class CheckAndAutoSyncUseCase:
    def __init__(self, user_id: str, token_data: dict):
        self.user_id = user_id
        self.token_data = token_data
        self.db = get_supabase()

    def execute(self):
        try:
            # 1. Đếm số lượng document trong DB
            response = self.db.table("documents").select("id", count="exact").eq("metadata->>user_id", self.user_id).execute()
            doc_count = response.count if hasattr(response, 'count') else 0
            
            # 2. Kiểm tra email mới từ Gmail
            gmail_service = GmailService(self.token_data)
            result = gmail_service.get_emails(max_results=50, folder="SENT")
            sent_emails = result.get('emails', [])
            
            if not sent_emails:
                return {
                    "synced": doc_count > 0,
                    "document_count": doc_count,
                    "pending_emails": 0,
                    "message": "Không tìm thấy email đã gửi nào"
                }

            # 3. So sánh với DB để tìm email chưa sync
            existing_rows = self.db.table("documents").select("metadata").eq("metadata->>user_id", self.user_id).execute()
            existing_email_ids = set()
            if existing_rows.data:
                for doc in existing_rows.data:
                    metadata = doc.get("metadata", {})
                    email_id = metadata.get("email_id")
                    if email_id:
                        existing_email_ids.add(email_id)

            new_email_ids = [e['id'] for e in sent_emails if e['id'] not in existing_email_ids]
            pending_count = len(new_email_ids)
            
            return {
                "synced": pending_count == 0,
                "document_count": doc_count,
                "pending_emails": pending_count,
                "message": "✓ Dữ liệu đã được đồng bộ hoàn toàn" if pending_count == 0 else f"Có {pending_count} email mới chưa đồng bộ"
            }
                
        except Exception as e:
            logging.error(f" [UseCase] Lỗi check status: {e}")
            # Fallback an toàn
            return {
                "synced": False,
                "document_count": 0,
                "message": f"Lỗi kiểm tra: {str(e)}"
            }