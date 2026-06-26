# Hướng dẫn sử dụng TransVideo

## 1. Cài đặt

1. Tải file `TransVideo-Web-Setup-4.03.exe` từ trang Release.
2. Mở file cài đặt và bấm Next cho đến khi hoàn tất.
3. Mở TransVideo từ Desktop hoặc Start Menu.
4. Lần đầu mở app, bấm **Tải runtime và mở app**.

Lần tải runtime đầu tiên có thể lâu vì app cần tải Python, PyTorch GPU/CPU và các thư viện AI. Các lần mở sau app sẽ chạy trực tiếp, không cần CMD.

## 2. Dịch video bằng link

1. Dán link video vào ô **Dịch video nhanh**.
2. Bật **Lồng tiếng** nếu muốn app tạo giọng đọc.
3. Giữ **Xóa video tạm** nếu muốn app xóa video nguồn tải tạm sau khi tạo final.
4. Bấm **Start**.
5. Video hoàn tất nằm trong thư mục `output/quick-videos` nếu bạn chưa chọn thư mục lưu khác.

## 3. Khi nào nên bật lồng tiếng?

- Tắt **Lồng tiếng** nếu chỉ cần phụ đề tiếng Việt chèn vào video.
- Bật **Lồng tiếng** nếu muốn video có giọng đọc tiếng Việt.
- Chất lượng giọng phụ thuộc vào kênh TTS bạn chọn. Giọng miễn phí thường không hay bằng các dịch vụ trả phí, nhưng có thể dùng để reup cơ bản.

## 4. Lỗi BiliBili HTTP 412 là gì?

Lỗi `HTTP Error 412: Precondition Failed` nghĩa là BiliBili từ chối cho công cụ tải metadata/video. Nguyên nhân thường gặp:

- Video cần đăng nhập hoặc cookie.
- Video bị giới hạn vùng.
- Link BiliBili đang chặn request tự động.
- Trình duyệt trên máy chưa từng mở hoặc phát video đó.

Cách xử lý:

1. Mở link video bằng Edge hoặc Chrome trên máy này.
2. Đăng nhập BiliBili nếu video yêu cầu.
3. Phát thử video vài giây.
4. Quay lại TransVideo và bấm Start lại.
5. Nếu vẫn lỗi, tải video thủ công rồi chọn file MP4 trong app.

## 5. Nếu lần tải runtime bị dừng giữa chừng

Nếu mất mạng, tắt máy, hoặc đóng app khi runtime đang tải, lần mở sau TransVideo sẽ báo phát hiện cài đặt dang dở.

Bạn bấm **Dọn cài lỗi**, sau đó bấm **Tải runtime và mở app** để tải lại sạch sẽ.

## 6. Gỡ cài đặt

Mở Start Menu, chọn **Uninstall TransVideo**. Trình gỡ cài đặt sẽ dọn app, runtime `.venv`, thư mục tạm, log, output và models đã tải trong thư mục cài đặt.
