# Workflow cho dự án Audio Transcription

## Workflow tổng quan

Dưới đây là workflow tổng quan cho dự án Audio Transcription, bao gồm cả library cốt lõi và ứng dụng demo:

```mermaid
flowchart TD
    subgraph "Input Sources"
        A1[Audio File Path]
        A2[BytesIO Object]
        A3[Audio Bytes]
    end
    
    subgraph "Core Library" 
        B1[AudioTranscriber]
        B2[TextAligner]
        B3[AudioProcessor]
    end
    
    subgraph "External Services"
        C1[Google Gemini API]
        C2[Stable Whisper Model]
    end
    
    subgraph "Output Processing" 
        D1[Transcription Results]
        D2[Alignment Results]
        D3[Combined Results]
    end
    
    subgraph "Demo UI"
        E1[Upload Interface]
        E2[Processing Controls]
        E3[Results Display]
        E4[Export Options]
        E5[Cache System]
    end
    
    A1 --> B3
    A2 --> B3
    A3 --> B3
    
    B3 --> B1
    B3 --> B2
    B1 --> C1
    B2 --> C2
    
    C1 --> D1
    C2 --> D2
    D1 --> D3
    D2 --> D3
    
    E1 -->|File Upload| A2
    B3 --> D3
    D3 --> E3
    E3 --> E4
    E5 -.->|Cache Results| D3
    E2 -->|Control Processing| B3
```

## Workflow xử lý audio

Chi tiết workflow cho quá trình xử lý audio từ upload đến kết quả:

```mermaid
sequenceDiagram
    actor User
    participant UI as Demo UI
    participant Processor as AudioProcessor
    participant Transcriber as AudioTranscriber
    participant Aligner as TextAligner
    participant GeminiAPI
    participant WhisperModel
    
    User->>UI: Upload audio file
    
    alt Cache available
        UI->>UI: Check cache
        UI-->>User: Return cached results
    else No cache
        UI->>Processor: process_audio()
        Processor->>Processor: _convert_to_mono()
        
        Processor->>Transcriber: transcribe()
        Transcriber->>Transcriber: _get_normalized_mime_type()
        Transcriber->>GeminiAPI: Upload file
        Transcriber->>GeminiAPI: Generate content
        
        GeminiAPI-->>Transcriber: Text + descriptions
        Transcriber->>Transcriber: _parse_response()
        Transcriber-->>Processor: Transcription results
        
        Processor->>Processor: _extract_transcript_text()
        
        Processor->>Aligner: align_text()
        Aligner->>WhisperModel: Align text with audio
        WhisperModel-->>Aligner: Word-level timestamps
        Aligner->>Aligner: Cut audio segments
        Aligner-->>Processor: Audio chunks + timestamps
        
        Processor->>Processor: _combine_results()
        Processor-->>UI: Final results
        
        UI->>UI: Cache results
        UI-->>User: Display results
        
        User->>UI: Download/Export
        UI-->>User: Results in selected format
    end
```

## Workflow retry và error handling

Chi tiết workflow cho xử lý lỗi API và retry mechanism:

```mermaid
flowchart TD
    A[API Call] --> B{Success?}
    B -->|Yes| C[Process Response]
    B -->|No| D{Error Type?}
    
    D -->|Rate Limit| E[Wait with exponential backoff]
    D -->|Model Overloaded| F[Wait longer]
    D -->|Other Errors| G[Simple retry]
    
    E --> H{Last attempt?}
    F --> H
    G --> H
    
    H -->|No| A
    H -->|Yes| I{Lite model?}
    
    I -->|Yes| J[Try with non-lite model]
    I -->|No| K[Return error]
    
    J --> L{Success?}
    L -->|Yes| C
    L -->|No| K
```

## Workflow giao diện người dùng

Chi tiết workflow cho tương tác người dùng với giao diện web:

```mermaid
flowchart TD
    A[Homepage] --> B[Navigation]
    
    B --> C[TTS Labeling]
    B --> D[Transcript View]
    
    C --> E[Settings]
    C --> F[Upload Form]
    
    E --> G[General Settings]
    E --> H[API Settings]
    E --> I[Advanced Settings]
    E --> J[Cache Settings]
    
    F --> K{Process?}
    K -->|Yes| L[Processing File]
    
    L --> M{Use Cache?}
    M -->|Yes| N[Fetch from Cache]
    M -->|No| O[Process File]
    
    N --> P[Display Results]
    O --> P
    
    P --> Q[Audio Segments]
    P --> R[Text Results]
    P --> S[Export Options]
    
    S --> T[Download Full Text]
    S --> U[Download ZIP]
    S --> V[Download JSON]
    
    D --> P
```

## Workflow deployment

Kế hoạch workflow cho deployment trong tương lai:

```mermaid
flowchart TD
    A[Local Development] --> B[Package Build]
    
    B --> C[Python Package]
    B --> D[Docker Image]
    
    C --> E[PyPI Publication]
    D --> F[Container Registry]
    
    E --> G[Library Users]
    F --> H[Docker Deployment]
    
    H --> I[Web Server]
    H --> J[API Server]
    H --> K[Database]
    
    I --> L[Load Balancer]
    J --> L
    
    L --> M[Users]
    M --> L
```

## Workflow model caching và optimization

Chi tiết về caching và optimization trong quá trình xử lý:

```mermaid
flowchart TD
    A[Audio Input] --> B{Cached?}
    
    B -->|Yes| C[Retrieve from Cache]
    B -->|No| D[Generate Cache Key]
    
    D --> E[AudioProcessor]
    
    E --> F[Transcription + Alignment]
    F --> G[Store in Cache]
    G --> H[Return Results]
    C --> H
    
    subgraph "Resource Management" 
        I[Model Loading]
        J[File Handling]
    end
    
    I -->|@st.cache_resource| E
    J -->|BytesIO Clean-up| E
```
