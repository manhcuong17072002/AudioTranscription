# Hướng dẫn xuất bản package lên PyPI

File này hướng dẫn cách xuất bản package `gemini_audio_transcription` lên PyPI.

## Chuẩn bị

1. Đảm bảo bạn đã cài đặt các công cụ cần thiết:

```bash
pip install build twine
```

2. Kiểm tra tệp cấu hình PyPI (nếu chưa có):

Tạo file `.pypirc` trong thư mục home của bạn:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = your-token-here

[testpypi]
username = __token__
password = your-testpypi-token-here
```

*Lưu ý: Thay thế `your-token-here` bằng token PyPI thực của bạn*

## Xây dựng package

1. Tạo bản distribution:

```bash
python -m build
```

Lệnh này sẽ tạo cả source distribution (.tar.gz) và wheel (.whl) trong thư mục `dist/`.

## Kiểm tra package

Trước khi upload lên PyPI, hãy kiểm tra package:

```bash
twine check dist/*
```

## Xuất bản lên TestPyPI (tùy chọn nhưng khuyến nghị)

TestPyPI là version thử nghiệm của PyPI, giúp bạn kiểm tra package trước khi xuất bản chính thức:

```bash
twine upload --repository testpypi dist/*
```

Sau khi upload, bạn có thể cài đặt package từ TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ gemini_audio_transcription
```

## Xuất bản lên PyPI chính thức

Khi bạn đã chắc chắn mọi thứ hoạt động tốt:

```bash
twine upload dist/*
```

## Cài đặt từ PyPI

Sau khi đã xuất bản thành công, người dùng có thể cài đặt package bằng pip:

```bash
pip install gemini_audio_transcription
```

Hoặc với các tính năng demo:

```bash
pip install "gemini_audio_transcription[demo]"
```

## Tips

- **Versioning**: Đảm bảo tăng version trong file `gemini_audio_transcription/version.py` mỗi khi xuất bản cập nhật
- **Clean build**: Xóa các bản build cũ trước khi tạo bản mới: `rm -rf dist/ build/ *.egg-info`
- **Git tag**: Tạo tag Git cho mỗi phiên bản: `git tag -a v0.1.0 -m "Initial release"`
