# Chatbot Fix Log — 2026-07-08

## Tổng quan

| # | File | Vấn đề | Mức độ |
|---|------|---------|--------|
| 1 | `tools/calculator.py` | `eval()` không an toàn | 🔴 Security |
| 2 | `tools/tool_registry.py` | `get()` crash với `KeyError` | 🟡 Stability |
| 3 | `tools/tool_executor.py` | Không có error handling | 🟡 Stability |
| 4 | `rag/chunker.py` | Cắt ký tự giữa chừng từ | 🟠 Quality |
| 5 | `rag/vector_store.py` | Metadata logic sai + thiếu dedup check | 🔴 Bug |
| 6 | `rag/retriever.py` | Re-index mỗi lần khởi động → duplicate data | 🔴 Bug |
| 7 | `responses.py` | Thiếu `tool_calls` list | 🟡 Feature |
| 8 | `models/groq_model.py` | Chỉ xử lý tool call đầu tiên | 🟡 Logic |
| 9 | `models/gemini_model.py` | Không có tool calling | 🟡 Feature |
| 10 | `models/openai_model.py` | Sai API + sai model name | 🔴 Crash |
| 11 | `chatbot.py` | Loop chỉ xử lý 1 tool/lượt | 🟡 Logic |
| 12 | `config.py` | Thiếu `OPENAI_MODEL_NAME` | 🟡 Config |
| 13 | `main.py` | chunk_size=100 quá nhỏ | 🟠 Quality |

---

## Chi tiết từng fix

### 1. `tools/calculator.py` — Thay `eval()` bằng AST evaluator an toàn
**Vấn đề:** `eval(expression)` cho phép model inject code tùy ý (ví dụ: `__import__('os').system('rm -rf /')`).

**Fix:** Implement `_safe_eval()` dùng `ast.parse()` + whitelist operators. Chỉ cho phép các phép tính số học (`+`, `-`, `*`, `/`, `**`, `%`, `//`). Mọi expression khác bị reject.

```diff
- def execute(self, expression):
-     return eval(expression)
+ def execute(self, expression: str):
+     try:
+         tree = ast.parse(expression, mode="eval")
+         result = self._safe_eval(tree.body)
+         return result
+     except Exception as e:
+         return f"Error evaluating expression: {e}"
```

---

### 2. `tools/tool_registry.py` — Xử lý tool không tồn tại
**Vấn đề:** `self.tools[name]` raise `KeyError` thô khi model hallucinate tên tool, crash app.

**Fix:** Thêm kiểm tra và raise lỗi có message rõ ràng kèm danh sách tools hợp lệ.

```diff
  def get(self, name: str):
+     if name not in self.tools:
+         available = list(self.tools.keys())
+         raise KeyError(f"Tool '{name}' not found. Available tools: {available}")
      return self.tools[name]
```

---

### 3. `tools/tool_executor.py` — Bọc tool execution trong try-except
**Vấn đề:** Không có error handling, mọi exception từ tool sẽ crash chatbot loop.

**Fix:** Bọc toàn bộ execute() trong try-except, trả về error string thay vì crash.

```diff
- tool = self.registry.get(tool_name)
- return tool.execute(**args)
+ try:
+     tool = self.registry.get(tool_name)
+     return tool.execute(**args)
+ except KeyError as e:
+     return f"Tool error: {e}"
+ except Exception as e:
+     return f"Tool '{tool_name}' execution failed: {e}"
```

---

### 4. `rag/chunker.py` — Sentence-aware chunking
**Vấn đề:** Cắt text theo ký tự thô → cắt giữa chừng từ → embedding chất lượng kém → RAG search kém.

**Fix:** Dùng `re.split()` để tách theo ranh giới câu (`.!?\n`), nhóm câu lại theo `chunk_size`, giữ overlap ký tự từ chunk trước.

---

### 5. `rag/vector_store.py` — Dedup check + metadata logic
**Vấn đề 1 (đã fix bởi user):** `metadatas is not len(texts)` — so sánh list với int luôn True.

**Vấn đề 2:** Thiếu method kiểm tra source đã được index chưa.

**Fix:** Thêm `is_source_indexed(source)` query ChromaDB theo metadata `source`.

```python
def is_source_indexed(self, source: str) -> bool:
    results = self.collection.get(where={"source": source}, limit=1)
    return len(results["ids"]) > 0
```

---

### 6. `rag/retriever.py` — Tránh duplicate khi re-index
**Vấn đề:** `index_file()` được gọi mỗi lần `main.py` khởi động → duplicate dữ liệu tích lũy trong ChromaDB → search bị lặp kết quả.

**Fix:** Kiểm tra `is_source_indexed()` trước khi index. Truyền `{"source": abs_path}` vào metadata để dedup theo file.

```diff
+ source = os.path.abspath(filepath)
+ if self.vector_store.is_source_indexed(source):
+     print(f"File '{filepath}' already indexed, skipping.")
+     return
  ...
+ metadatas = [{"source": source} for _ in chunks]
  self.vector_store.add(chunks, embeddings, metadatas=metadatas)
```

---

### 7. `responses.py` — Thêm `tool_calls` list
**Vấn đề:** `ChatResponse` chỉ có `tool_call` (single) → không support parallel tool calls.

**Fix:** Thêm `tool_calls: List[ToolCall] | None = None`. Giữ `tool_call` cho backward compat.

---

### 8. `models/groq_model.py` — Xử lý tất cả tool calls
**Vấn đề:** `tool_call = message.tool_calls[0]` — bỏ qua tool calls từ index 1 trở đi.

**Fix:** List comprehension qua toàn bộ `message.tool_calls`, populate cả `tool_calls` lẫn `raw_tool_calls`.

---

### 9. `models/gemini_model.py` — Thêm tool calling support
**Vấn đề:** Không có tool calling → crash hoặc trả lời sai khi model cần dùng tool.

**Fix:**
- `_build_gemini_tools()`: convert schema OpenAI format → `types.FunctionDeclaration`
- `convert_messages()`: xử lý assistant message có tool calls và tool response messages
- `chat()`: detect `response.function_calls` và trả về `ChatResponse` với tool info
- raw_tool_calls lưu theo Gemini format: `[{"name": ..., "args": {...}}]`

---

### 10. `models/openai_model.py` — Sửa API sai
**Vấn đề:**
- Dùng `client.responses.create()` thay vì `client.chat.completions.create()`
- `convert_messages()` trả về tuple `(contents, system_prompt)` nhưng bị pass trực tiếp vào `input=`
- Model name `gpt-5.5` không tồn tại
- Không có tool calling support

**Fix:** Rewrite theo pattern Groq (chat.completions.create + xử lý tool calls đầy đủ).

---

### 11. `chatbot.py` — Loop xử lý tất cả tool calls
**Vấn đề:** Check `response.tool_call is None` → chỉ xử lý 1 tool call.

**Fix:** Check `response.tool_calls` (list), loop qua tất cả và append từng tool result vào history.

```diff
- if response.tool_call is None:
+ if not response.tool_calls:
      ...
  else:
-     tc = response.tool_call
-     # execute tc
+     for tc in response.tool_calls:
+         # execute tc, append to history
```

---

### 12. `config.py` — Thêm OPENAI_MODEL_NAME
```diff
+ OPENAI_MODEL_NAME = "gpt-4o"
```

---

### 13. `main.py` — Tăng chunk_size
Phù hợp với sentence-aware chunker mới (100 ký tự quá nhỏ, hay cắt giữa câu).
```diff
- retriever = Retriever(embedder, vector_store, chunk_size=100, overlap=50)
+ retriever = Retriever(embedder, vector_store, chunk_size=500, overlap=100)
```

---

## Lưu ý: Xóa chroma_db cũ
Vì dữ liệu cũ đã bị duplicate từ các lần chạy trước, cần xóa và re-index:
```bash
rm -rf ./chroma_db
```
Lần chạy tiếp theo sẽ tự động index lại với chunk quality tốt hơn.
