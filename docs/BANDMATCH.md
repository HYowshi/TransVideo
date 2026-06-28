# BandMatch

`videotrans/bandmatch` là lớp tính toán nhịp phụ đề/thoại cho TransVideo.

Mục tiêu:

- Đo độ dày chữ trong từng dòng phụ đề.
- Ước lượng thời lượng TTS cần để đọc tự nhiên.
- So với slot thời gian gốc để biết câu nào dễ bị đọc quá dài.
- Đề xuất preset đồng bộ: tăng tốc giọng, nới timeline video, xóa khoảng lặng hoặc căn audio/sub.

Hiện tại BandMatch được dùng ở hai nơi:

1. Workflow nhanh dùng preset bảo thủ cho video Trung -> Việt khi bật lồng tiếng.
2. Pipeline lồng tiếng phân tích `queue_tts` thật và ghi điểm vào log để tiếp tục tối ưu.

Các chỉ số chính:

- `score`: 0-100, càng cao càng dễ đồng bộ.
- `p90_pressure`: áp lực đọc ở nhóm dòng nặng nhất. Trên `1.0` nghĩa là ước lượng đọc dài hơn slot.
- `risky_ratio`: tỷ lệ dòng có nguy cơ lệch nhịp.
- `overlap_count`: số dòng bị overlap timeline.

BandMatch chưa thay thế toàn bộ logic đồng bộ cũ. Nó là lớp đo và đề xuất để tối ưu dần mà không làm pipeline hiện tại mất ổn định.
