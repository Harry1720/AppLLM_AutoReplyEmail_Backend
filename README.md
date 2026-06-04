# Trợ lý Email Thông minh - Backend

Đây là kho lưu trữ mã nguồn Backend cho dự án **Trợ lý Email Thông minh** - một ứng dụng website hỗ trợ tự động gợi ý bản nháp trả lời email dựa trên văn phong cá nhân của người dùng.

Hệ thống được xây dựng bằng **FastAPI**, kết hợp với Trí tuệ Nhân tạo (LLM thông qua hệ sinh thái **LangChain/LangGraph**) để tự động đồng bộ, phân tích và tạo ra các phản hồi email thông minh từ tài khoản Gmail của người dùng. Dự án áp dụng **Clean Architecture**, giúp mã nguồn dễ bảo trì, mở rộng và kiểm thử.

# Mục lục

- [1. Các tính năng chính](#1-các-tính-năng-chính)
- [2. Công nghệ sử dụng](#2-công-nghệ-sử-dụng)
- [3. Cấu trúc thư mục lõi (Clean Architecture)](#3-cấu-trúc-thư-mục-lõi-clean-architecture)
- [4. Hướng dẫn cài đặt \& khởi chạy vắn tắt (Local)](#4-hướng-dẫn-cài-đặt--khởi-chạy-vắn-tắt-local)
  - [4.1. Yêu cầu hệ thống](#41-yêu-cầu-hệ-thống)
  - [4.2. Thiết lập môi trường ảo](#42-thiết-lập-môi-trường-ảo)
  - [4.3. Cấu hình biến môi trường](#43-cấu-hình-biến-môi-trường)
  - [4.4. Chạy ứng dụng Server](#44-chạy-ứng-dụng-server)
  - [4.5. Tài liệu API (Swagger UI)](#45-tài-liệu-api-swagger-ui)
- [5. Các endpoint API chính](#5-các-endpoint-api-chính)
- [6. Tài liệu dự án](#6-tài-liệu-dự-án)
- [7. Lỗi thường gặp](#7-lỗi-thường-gặp)
- [8. Thực hiện](#8-thực-hiện)
- [9. Mã nguồn Frontend của dự án](#9-mã-nguồn-frontend-của-dự-án)


## 1. Các tính năng chính

- **Xác thực Google (OAuth2):** Đăng nhập an toàn bằng tài khoản Google và cấp quyền truy cập xử lý hộp thư Gmail.
- **Đồng bộ Email:** Tự động fetch và đồng bộ hộp thư đến từ Gmail về hệ thống.
- **AI Agent sinh phản hồi:** Phân tích ngữ cảnh email và tự động soạn thảo câu trả lời tự nhiên, phù hợp bằng cách sử dụng sức mạnh của **Groq LLM** **_(mô hình Llama 3.3 70B Versatile)_** và **LangGraph**.
  - **Pipeline AI trả lời Email (LangGraph Workflow):** Gồm 4 bước: (1) Lấy email gốc -> (2) Tìm kiếm ngữ cảnh RAG -> (3) LLM tạo phản hồi -> (4) Lưu bản nháp vào Gmail & Database.
- **Vector Search, học văn phong & xử lý AI:** Chạy Background Tasks quét email đã gửi, chia nhỏ (chunking), sử dụng **Sentence Transformers** để tạo vector embeddings cho email/tài liệu, lưu vào **Supabase** để hỗ trợ AI truy xuất thông tin (RAG), "học" phong cách viết nhằm trả lời chính xác hơn.
- **Tối ưu khởi động:** Tải ngầm model AI (background preload) ngay lúc server startup, triệt tiêu độ trễ cho các API request đầu tiên.
- **Lưu trữ:** Tích hợp **Supabase** để lưu trữ người dùng, dữ liệu email và dữ liệu vector.
- **RESTful API:** Cung cấp các endpoints chuẩn hóa tại /auth, /emails, /ai, và /users.
- **Bảo mật dữ liệu:** Áp dụng Row Level Security (RLS) của Supabase đảm bảo tính cô lập dữ liệu cho từng người dùng

## 2. Công nghệ sử dụng

- **Backend Framework:** Python 3.10+, FastAPI, Uvicorn.
- **Cơ sở dữ Liệu:** PostgreSQL (triển khai qua Supabase) tích hợp extension `pgvector` 0.5.1 để lưu trữ vector.
- **AI & LLM:**
  - LangChain 0.3.x và LangGraph 0.2.x để xây dựng luồng xử lý Agentic
  - Mô hình Llama 3.3 70B Versatile thông qua Groq Cloud API.
  - Sentence-Transformers, HuggingFace.
- **Tích hợp bên thứ 3:** Google Workspace APIs (Gmail API, Google Auth).

## 3. Cấu trúc thư mục lõi (Clean Architecture)

Dự án được phân tách thành các module rõ ràng:

- `app/api/`: Chứa các Router định tuyến HTTP requests (Auth, Email, User, AI).
- `app/use_case/`: Tầng chứa logic nghiệp vụ chính (VD: `GenerateReplyUseCase`, `SyncEmailsUseCase`).
- `app/domain/`: Định nghĩa các Entities dữ liệu và Repositories Interfaces.
- `app/infra/`: Các cơ sở hạ tầng giao tiếp bên ngoài (Supabase Client, Gmail Service, cấu hình Model AI).

## 4. Hướng dẫn cài đặt & khởi chạy vắn tắt (Local)

Để có hướng dẫn chi tiết hơn, xem [Tài liệu dự án](#6-tài-liệu-dự-án), phần tài liệu hướng dẫn

### 4.1. Yêu cầu hệ thống

- Python 3.10 trở lên.
- Đã đăng ký và lấy key từ:
  - **Supabase** (Tạo project mới).
  - **Google Cloud Console** (Tạo OAuth2 Client ID cho Web application).
  - **Groq Console** (Lấy API Key).

### 4.2. Thiết lập môi trường ảo

```bash
# Clone dự án về máy, sau đó tạo môi trường ảo (Virtual Environment)
python -m venv venv

# Kích hoạt môi trường (Trên Windows)
venv\Scripts\activate
# Trên MacOS/Linux: source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 4.3. Cấu hình biến môi trường

Tạo file `.env` từ file mẫu:

```bash
cp .env.example .env
```

Mở file `.env` và điền đầy đủ thông tin:

- `SUPABASE_URL` & `SUPABASE_SERVICE_KEY`
- `JWT_SECRET` (Tự sinh một chuỗi ngẫu nhiên)
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`
- `GROQ_API_KEY`

### 4.4. Chạy ứng dụng Server

```bash
uvicorn app.main:app --reload
```

- Hệ thống sẽ chạy tại cổng `8000`. Khi khởi động, bạn sẽ thấy log tải các model AI chạy ngầm.

- Check trạng thái sẵn sàng tại: `http://localhost:8000/ready`

### 4.5. Tài liệu API (Swagger UI)

- FastAPI cung cấp giao diện Swagger UI tuyệt vời để xem và kiểm thử trực tiếp các endpoint API.

- Truy cập: **[http://localhost:8000/docs](http://localhost:8000/docs)**

## 5. Các endpoint API chính

Hệ thống được chia thành các cụm tính năng:

- **`[Auth]` - `/auth/...`**: Xử lý đăng nhập, callback Google OAuth2.
- **`[Email]` - `/emails/...`**: Đồng bộ, lấy danh sách email, kiểm tra tiến độ đồng bộ.
- **`[AI Agents]` - `/ai/...`**: Kích hoạt Agent, yêu cầu sinh phản hồi (draft) cho email.
- **`[User]` - `/users/...`**: Quản lý thông tin hồ sơ và cấu hình người dùng.

## 6. Tài liệu dự án

- [Báo cáo](/frontend/DOCS/22H1120002_22H1120095_DeTai6_BaoCaoTTTN.pdf)
- [Hướng dẫn sử dụng](/frontend/DOCS/22H1120002_22H11200095_TaiLieuHDSD_DeTai6.pdf)
- [Hướng dẫn cài đặt](/frontend//DOCS/22H1120002_22H11200095_TaiLieuCaiDat_DeTai6.pdf)

## 7. Lỗi thường gặp

Trong quá trình cài đặt và chạy dự án, bạn có thể gặp một số lỗi phổ biến sau:

- **Lỗi `ModuleNotFoundError` khi khởi chạy:**
  - *Nguyên nhân:* Chưa cài đặt đầy đủ các thư viện phụ thuộc hoặc chưa kích hoạt môi trường ảo.
  - *Khắc phục:* Kích hoạt môi trường ảo (ví dụ: `venv\Scripts\activate` trên Windows) và chạy lệnh `pip install -r requirements.txt`.

- **Lỗi không kết nối được với Supabase / PostgreSQL:**
  - *Nguyên nhân:* Sai cấu hình `SUPABASE_URL` hoặc `SUPABASE_SERVICE_KEY` trong file `.env`.
  - *Khắc phục:* Kiểm tra lại thông tin cấu hình từ trang quản trị Supabase và cập nhật chính xác vào `.env`.

- **Lỗi `redirect_uri_mismatch` khi đăng nhập Google OAuth2:**
  - *Nguyên nhân:* Callback URL được cấu hình trong Google Cloud Console không khớp với URL của dự án.
  - *Khắc phục:* Đảm bảo thêm chính xác URI (thường là `http://localhost:8000/auth/callback` hoặc tương tự) vào phần "Authorized redirect URIs" trong dự án Google Cloud Console.

- **Lỗi liên quan đến Groq API (Rate limit / Invalid API Key):**
  - *Nguyên nhân:* Hết hạn mức gọi API hoặc API Key không hợp lệ.
  - *Khắc phục:* Kiểm tra lại `GROQ_API_KEY` trong file `.env` hoặc truy cập trang Groq Console để kiểm tra trạng thái API key.

- **Lỗi cổng 8000 đã được sử dụng (Port in use):**
  - *Nguyên nhân:* Có một dịch vụ khác đang sử dụng cổng 8000 trên máy.
  - *Khắc phục:* Đổi sang cổng khác bằng cách thêm tham số vào lệnh chạy: `uvicorn app.main:app --reload --port 8080`.

## 8. Thực hiện

- Huỳnh Nguyễn Quốc Bảo
- Phí Ngọc Thái Bình

*Trường Đại học Giao thông Vận tải TP.HCM*

## 9. Mã nguồn Frontend của dự án

Truy cập: <https://github.com/Harry1720/AppLLM_AutoReplyEmail_Frontend>
