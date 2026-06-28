# Code signing cho TransVideo

Windows SmartScreen và trình duyệt thường cảnh báo file `.exe` mới nếu file chưa có uy tín tải về hoặc chưa được ký bằng chứng chỉ code-signing đáng tin cậy.

Repo này đã chuẩn bị sẵn workflow ký số:

- `WINDOWS_CERTIFICATE_PFX`: nội dung file `.pfx` đã base64.
- `WINDOWS_CERTIFICATE_PASSWORD`: mật khẩu của file `.pfx`.

Khi hai secret này tồn tại, GitHub Actions sẽ ký:

1. `TransVideo.exe`
2. `TransVideo-Web-Setup-1.0.exe`

## Tạo base64 từ PFX trên PowerShell

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\certificate.pfx")) | Set-Clipboard
```

Sau đó dán chuỗi vào GitHub repo secret `WINDOWS_CERTIFICATE_PFX`.

## Lưu ý

- Chứng chỉ OV code-signing giúp giảm cảnh báo dần khi app có uy tín.
- Chứng chỉ EV code-signing thường được SmartScreen tin nhanh hơn, nhưng đắt hơn và cần phần cứng/token hoặc cloud HSM.
- Không nên dùng chứng chỉ tự ký cho release công khai vì Windows vẫn xem là không đáng tin.
