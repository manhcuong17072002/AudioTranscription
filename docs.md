# Generate text using the Gemini API
## Generate text from text-only input
```python
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Write a story about a magic backpack.")
print(response.text)
```
> Có thể sử dụng thêm cac kỹ thuật prompt khác như one-shot hay few-shot learning để model có thể trả về đầu ra theo mong muốn. Ngoài ra ta có thể thêm `system instructuon` để giúp model hiểu hơn về task hay đi theo guidelines đã được chỉ định

## Generate text from text-and-image input
Gemini cũng hỗ trợ nhiều đầu vào mà kết hợp text với media files như:
```python
import PIL.Image

model = genai.GenerativeModel("gemini-2.0-flash")
organ = PIL.Image.open(media / "organ.jpg")
response = model.generate_content(["Tell me about this instrument", organ])
print(response.text)
```
> Gemini chỉ nhận ảnh thông qua `upload file` hay `PIL.Image` làm đầu vào và không nhận các dạng khác như `bytes` hay `BytesIO`

## Generate a text stream
```python
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Write a story about a magic backpack.", stream=True)
for chunk in response:
    print(chunk.text)
    print("_" * 80)
```

## Build an interactive chat
Bạn có thể sử dụng Gemini API để tạo cuộc trò chuyện giữa chatbot và người dùng. Sử dụng tính năng chat của API ncho phép bạn có thể sử dụng history để từng bước đạt được câu trả lời hoặc giúp đỡ nhiều vấn đề cùng một lúc. Tính năng này là lý tưởng cho ứng dụng mà yêu cầu tương tác liên tục như là chatbots, hướng dẫn viên hoặc trợ lý hỗ trợ khách hàng
```python
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(
    history=[
        {"role": "user", "parts": "Hello"},
        {"role": "model", "parts": "Great to meet you. What would you like to know?"},
    ]
)
response = chat.send_message("I have 2 dogs in my house.")
print(response.text)
response = chat.send_message("How many paws are in my house?")
print(response.text)
```

## Configure text generation
Mỗi prompt bạn gửi tới model bao gồm các `params` mà kiểm soát cách model tạo ra responses.
```python
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content(
    "Tell me a story about a magic backpack.",
    generation_config=genai.types.GenerationConfig(
        # Only one candidate for now.
        candidate_count=1, # số câu trả lời được tạo ra
        stop_sequences=["x"], # chuỗi kh được bao gồm trong response, nếu được chỉ định, API sẽ dừng tạp ra response ngay từ lần xuất hiện của chuỗi 
        max_output_tokens=20,
        temperature=1.0,
    ),
)

print(response.text)
```

hoặc
```python
response = model.generate_content(
    'Write a story about a magic backpack.',
    generation_config = genai.GenerationConfig(
        max_output_tokens=1000,
        temperature=0.1,
    )
)
```

# Explore vision capabilities with the Gemini API
## Technical details (images)
Gemini 1.5 Pro và 1.5 Flash chỉ hỗ trợ tối đa 3600 file ảnh. Một số loại được hỗ trợ như: 
- PNG: image/png
- JPEG: image/jpeg
- WEBP: image/webp
- HEIC: image/heic
- HEIF: image/heif

Mỗi ảnh tương ứng 258 tokens. Ảnh lớn sẽ được scale down xuống tối đa là: `3072x3072` và ảnh có kích thước nhỏ sẽ được scale up lên tối thiểu `768x768`, và vẫn được giữ nguyên tỉ lệ giữa 2 cạnh

> Giá không đổi với mọi kích thước hình ảnh
> Không nên để `Temperature = 0, top_p = 0` để cố gắng nhất quán đầu ra bởi vì nó có thể ảnh hướng tới tốc độ của đầu ra

Best practices:
- Xoay hình ảnh theo đúng hướng trước khi tải lên.
- Ảnh không được mờ, nhòe, noise
- Nếu sử dụng `1 ảnh`, đặt text prompt sau ảnh

## Upload an image and generate content
Sử dụng `media.upload` để upload ảnh với bất kỳ kích thước nào

> Nếu `instruction + file` có kích thước lớn hơn `20MB`, thì sử dụng `File API` thay vì truyền thẳng `Image.Image` vào như là một prompt

> File API cho phép bạn lưu trữ 20GB cho mỗi project và mỗi file có kích thước tối đa là 2GB. File được lưu trữ trong 48 giờ và bạn có thể truy cập vào file trong thời gian đó nhưng bạn sẽ không thể tải chúng từ API. `Nó có sẵn và không mất phí ở mọi quốc gia mà Gemini API được hỗ trợ`

Sau khi ta upload file bằng API, ta có thể sử dụng `file + text prompt` như sau:
```python
myfile = genai.upload_file(media / "Cajun_instruments.jpg")
print(f"{myfile=}")

model = genai.GenerativeModel("gemini-2.0-flash")
result = model.generate_content(
    [myfile, "\n\n", "Can you tell me about the instruments in this photo?"]
)
print(f"{result.text=}")
```

Nếu ta chỉ cần upload file có kích thước nhỏ, ta có thể sử dụng gọi trực tiếp từ Gemini API:
```python
from PIL import Image
from io import BytesIO

image = Image.open("image.jpg")

prompt = """
"""

response = model.generate_content([image, prompt])
```

## Verify image file upload and get metadata
Bạn cũng có thể kiểm tra xem API đã lưu trữ bạn tải lên thành công hay chưa và lấy metadata của chúng bằng cách `files.get`. Và mỗi file chỉ có một tên duy nhất

```python
myfile = genai.upload_file(media / "poem.txt")
file_name = myfile.name
print(file_name)  # "files/*"

myfile = genai.get_file(file_name)
print(myfile)
```
# Prompt với nhiều ảnh 
Bạn có thể prompt với nhiều ảnh như sau:
```python
# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

prompt = "Write an advertising jingle showing how the product in the first image could solve the problems shown in the second two images."

response = model.generate_content([prompt, sample_file, sample_file_2, sample_file_3])
```

## Get a bounding box for an object
Bạn có thể yêu cầu model tìm tọa độ bbox của đối tượng trong ảnh. 
```python
# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

prompt = "Return a bounding box for the piranha. \n [ymin, xmin, ymax, xmax]"
response = model.generate_content([piranha, prompt])

print(response.text)
```
Tuy nhiên kết quả của mô hình đang ở kích thước ảnh 1000x1000, vì vậy ta cần phải thực hiện một số bước hậy xử lý như sau:
- Chia tọa độ của bbox cho 1000
- Nhân tọa độ tương ứng với chiều dài và chiều rông của ảnh gốc
## Prompting with video
Gemini 1.5 Pro và 1.5 Flash hỗ trợ video có độ dài lên tới `1 tiếng`. Video phải là một trong những loại MIME types sau:
- video/mp4
- video/mpeg
- video/mov
- video/avi
- video/x-flv
- video/mpg
- video/webm
- video/wmv
- video/3gpp
File API sẽ chia video ra thành 2 phần là khung hình và âm thanh. File API sẽ trích xuất nội dung với tỉ lệ 1 FPS đối với video và 1kbps đối với audio, trên 1 channel và đánh dấu timestamps tại mỗi giây. Những tỷ lệ này sẽ có thể sẽ thay đổi để cải thiện khả năng suy luận của mô hình
> Với các chi tiết hành động nhanh có thể bị bỏ xót nếu chỉ sử dụng tỉ lệ lấy mẫu 1 FPS. Hãy cân nhắc làm giảm tốc độ của video để cải thiện chất lượng hiểu của model

Tương tự như ảnh, mỗi frame tiêu tốn 258 tokens và 32 tokens với 1s audio. Do đó 1s video ~ 300 tokens.

Ta có thể đặt câu hỏi tại một thời điểm nhất định trong video bằng cách sử dụng format `MM:SS` tương ứng với phút và giây mà ta muốn hỏi

```python
# Create the prompt.
prompt = "What are the examples given at 01:05 and 01:19 supposed to show us?"

# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# Make the LLM request.
print("Making LLM inference request...")
response = model.generate_content([prompt, video_file],
                                  request_options={"timeout": 600})
print(response.text)
```

Best practices:
- Sử dụng 1 video/prompt
- Nếu sử dụng 1 video cho prompt, hãy đặt text prompt sau video

Upload video trực tiếp bằng `File API` như sau:
```python
# Upload the video and print a confirmation.
video_file_name = "GreatRedSpot.mp4"

print(f"Uploading file...")
video_file = genai.upload_file(path=video_file_name)
print(f"Completed upload: {video_file.uri}")
```

Và ta cũng có thể kiểm tra xem video có được upload thành công hay không:
```python
import time

# Check whether the file is ready to be used.
while video_file.state.name == "PROCESSING":
    print('.', end='')
    time.sleep(10)
    video_file = genai.get_file(video_file.name)

if video_file.state.name == "FAILED":
  raise ValueError(video_file.state.name)
```
> Note: Video files có 1 trường `State` trong `File API`. Khi mà một video được upload, nó sẽ trong trạng thái `PROCESSING` cho đến khi sẵn sàng để suy luận trên video. Chỉ những video được upload thành công mới có thể được sử dụng cho model inference.


# Explore document processing capabilities with the Gemini API
## Technical details
Gemini hỗ trợ tối đa 3600 trang tài liệu. Mỗi trang tài liệu phải là dữ liệu `text` có MIME type như sau:
- PDF - application/pdf
- JavaScript - application/x-javascript, text/javascript
- Python - application/x-python, text/x-python
- TXT - text/plain
- HTML - text/html
- CSS - text/css
- Markdown - text/md
- CSV - text/csv
- XML - text/xml
- RTF - text/rtf
> Mỗi trang tài liệu tương đương với 258 tokens

Không có giới hạn nào về số lượng pixel trong documetn, nếu page mà lớn sẽ được scaled down xuống độ phân giải 3072x3072, và pages có kích thước nhỏ thì được scaled up lên 768x768 trong khi vẫn giữ lại ratio của ảnh.
> Giống gửi file ảnh. tuy nhiên không rõ liệu rằng Gemini API có convert documents sang images hay không.

Best practice:
- Pages phải được xoay theo đúng hướng trước khi tải lên.
- Tránh pages bị mờ
- Nếu chỉ sử dụng 1 page duy nhất, hãy đặt text prompt ở sau page

## Upload a document and generate content
> Tương tự như upload ảnh.

```python
model = genai.GenerativeModel("gemini-2.0-flash")
sample_pdf = genai.upload_file(media / "test.pdf")
response = model.generate_content(["Give me a summary of this pdf file.", sample_pdf])
print(response.text)
```

## Get metadata for a file
Tương tự như khi upload ảnh. Bạn có thể kiểm tra xem file đã được đẩy lên thành công hay chưa:
```python
myfile = genai.upload_file(media / "poem.txt")
file_name = myfile.name
print(file_name)  # "files/*"

myfile = genai.get_file(file_name)
print(myfile)
```

## Upload one or more locally stored files
Nếu bạn muốn sử dụng kết hợp nhiều file cùng với `system instruction` có kích thước lớn hơn 20MB. Thì hãy sử dụng uploadfile như ở trên. Nếu với file nhỏ hơn, bạn có thể gọi cục bộ từ Gemini API:
```python
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text

sample_file_2 = extract_text_from_pdf('example-1.pdf')
sample_file_3 = extract_text_from_pdf('example-2.pdf')
```
## Prompt with multiple documents
```python
# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

prompt = "Summarize the differences between the thesis statements for these documents."

response = model.generate_content([prompt, sample_file, sample_file_2, sample_file_3])

print(response.text)
```

# List files
Bạn có thể liệt kê tất cả các file đã được upload sử dụng `files.list`
```python
print("My files:")
for f in genai.list_files():
    print("  ", f.name)
```

# Delete files
Tấ cả các files sẽ được tự động xóa sau 2 ngày. Bạn có thể xóa thủ công chúng bằng cách sử dụng `files.delete`
```python
myfile = genai.upload_file(media / "poem.txt")

myfile.delete()

try:
    # Error.
    model = genai.GenerativeModel("gemini-2.0-flash")
    result = model.generate_content([myfile, "Describe this file."])
except google.api_core.exceptions.PermissionDenied:
    pass
```