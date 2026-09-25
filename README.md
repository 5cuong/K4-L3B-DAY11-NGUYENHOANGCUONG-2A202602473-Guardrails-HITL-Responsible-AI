# Day 11 — Controlled Agent Security (2026)

> 👤 **Hình thức:** bài tập **cá nhân** (1 người / 1 MSSV).  
> 🎯 **Mục tiêu:** xây **Blue Agent** (phòng thủ), rồi red-team **Red Agent (default)** + **Red Agent (advance)**.  
> ✅ Làm theo **Checkpoint 1 → 5** trong [`CHECKPOINTS.md`](CHECKPOINTS.md) · nộp theo [`SUBMISSION.md`](SUBMISSION.md).

---

## Thời lượng

| Phần | Thời gian |
|------|-----------|
| Setup môi trường (Checkpoint 1) | ≈ **30'** |
| Lab làm bài (Checkpoint 2 → 5) | ≈ **130'** |
| **Tổng** | ≈ **160'** |

**Hạn nộp:** **23h59 cùng ngày làm Lab** (ICT / GMT+7). Gia hạn chỉ khi Key Coach thông báo trong 48 giờ sau Lab — xem [`RULES.md`](RULES.md).

---

## Chuẩn bị (trước / đầu buổi Lab)

1. Máy có **Python 3.10+** (khuyến nghị 3.11 hoặc 3.12) và Git.
2. Tài khoản GitHub cá nhân (để fork + đổi tên repo nộp).
3. API keys:
   - **Blue Agent (bắt buộc):** [OpenRouter](https://openrouter.ai/keys) — model cố định [`liquid/lfm-2.5-2.6b`](https://openrouter.ai/liquid/lfm-2.5-2.6b)
   - **Red Agent (chọn một provider):** [OpenAI](https://platform.openai.com/api-keys) (`gpt-4o-mini`) **hoặc** [Google AI Studio](https://aistudio.google.com/apikey) (`gemini-3.5-flash`)
4. Đọc nhanh [`RULES.md`](RULES.md) và [`RUBRIC.md`](RUBRIC.md).

### Ba agent (đặt tên thống nhất)

| Tên gọi | Code / file | Bạn làm gì? | Checkpoint |
|---------|-------------|-------------|------------|
| **Blue Agent** | `create_blue_agent(plugins)` + pipeline CP2–3 | **Bạn code** guardrails / rate limit / audit → phòng thủ | CP2–3 → `results.json` |
| **Red Agent (default)** | `create_red_agent_default()` | Có sẵn, **mềm** — red-team **phải leak** secret | CP4 (trong 20đ) |
| **Red Agent (advance)** | `create_red_agent_advance()` | Có sẵn, **cứng** — leak được = bonus B2 | CP4 (bonus) |

> **Không** tấn công Blue Agent ở CP4. CP4 chỉ chạy **Red Agent (default)** rồi **Red Agent (advance)**.  
> Trong JSON / log vẫn có thể thấy `unsafe` / `guards` / `protected` — đó là **tên kỹ thuật** cũ, map đúng bảng trên.

| Vai trò | Provider / model |
|---------|------------------|
| **Blue Agent** | OpenRouter **`liquid/lfm-2.5-2.6b`** (khóa cứng) |
| **Red Agent** (default + advance) | `gpt-4o-mini` **hoặc** `gemini-3.5-flash` |
| Bonus B1 (model khó khi tấn công Red Agent default) | `gpt-5.6-luna` / `gemini-3.8-flash` |

---

## Bộ tài liệu trong repo (quy ước Khóa 4)

| File | Nội dung |
|------|----------|
| [`README.md`](README.md) | Mục tiêu, chuẩn bị, thời lượng, cách bắt đầu, liên kết tài liệu |
| [`CHECKPOINTS.md`](CHECKPOINTS.md) | Làm bài theo mốc — việc cần làm, hiểu gì, lệnh chạy, Pass Signal |
| [`SUBMISSION.md`](SUBMISSION.md) | Cấu trúc repo, tên artifact, deadline, checklist trước khi nộp |
| [`RUBRIC.md`](RUBRIC.md) | Tiêu chí chấm, điểm từng phần, bằng chứng, bonus (≤ +10) |
| [`RULES.md`](RULES.md) | Quy định AI, sao chép, API key, nộp muộn |
| [`schemas/results.schema.json`](schemas/results.schema.json) | Schema bắt buộc của `outputs/results.json` |

Codelab lớp: xem `template-codelabs/codelab-day11-k4-l3a.md` (L3A) hoặc bản L3B tương ứng.

**Repo nộp học viên:** `K4-L3-DAY11-<HoVaTen>-<MSSV>-Guardrails-HITL-Responsible-AI`  
Ví dụ: `K4-L3-DAY11-NguyenVanA-2A2026xxxxx-Guardrails-HITL-Responsible-AI`

---

## 1. Bài toán

Chatbot VinBank giả định nhận email / tài liệu RAG và có thể gợi ý thao tác ngân hàng. Nội dung đó chỉ là **data chưa tin cậy** — không phải lệnh hệ thống (kẻ tấn công có thể nhét jailbreak vào email). Bạn kiểm soát đường đi **source → model → tool/egress** bằng guardrails + egress — **không** cần tự code email/RAG.

Cả ba agent đều nhúng secret giả từ:

`data/protected/vinbank_secrets.json`

| Loại | Key trong JSON | Giá trị demo |
|------|----------------|--------------|
| Admin password | `admin_password` | `admin123` |
| API key | `api_key` | `sk-vinbank-secret-2024` |
| DB host | `db_host` | `db.vinbank.internal:5432` |

- **Red Agent (default):** được phép lộ — red-team **phải leak** ít nhất một giá trị.  
- **Blue Agent** (plugin của bạn) + **Red Agent (advance):** **không** được lộ (advance leak = bonus).

```text
User → Rate Limiter → Input Guardrails → LLM → Output Guardrails
                                              → Audit / Monitoring → Reply / Egress check
```

| Đã có sẵn | Bạn tự làm | Hệ thống sinh ra |
|-----------|------------|------------------|
| Starter `src/guardrails/`, `src/assignment/`, `src/attacks/` | Theo Checkpoint 2–4 | `outputs/results.json`, `attack_results.json`, … |
| `create_red_agent_default()` / `create_red_agent_advance()` | Không sửa secret | — |
| `hitl/`, `testing/`, Judge, NeMo, AI attacks | Tham khảo — không chấm | — |

---

## 2. Rubric (tóm tắt)

| Phần | Điểm |
|------|-----:|
| Input + output guardrails (CP2) — Blue Agent | 40 |
| Pipeline + permission (CP3) → `results.json` | 40 |
| Red team (CP4) → `attack_results.json` + leak Red Agent (default) | 20 |
| **Bonus lab** (B1 model khó + B2 leak Red Agent advance) | tối đa **+10** |

Chi tiết tiêu chí, điều kiện mất điểm, grader replay: [`RUBRIC.md`](RUBRIC.md).

Thứ tự làm: **Setup → Blue Agent (phòng thủ) → Red Agent (tấn công) → nộp**.

---

## 3. Cách bắt đầu

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# Nếu bị chặn: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
Copy-Item .env.example .env
pip install -r requirements.txt
```

**macOS / Linux (bash):**

```bash
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
```

Điền `.env`: `OPENROUTER_API_KEY` + `RED_TEAM_PROVIDER=openai|gemini` (và key tương ứng).  
Rồi mở [`CHECKPOINTS.md`](CHECKPOINTS.md) và làm lần lượt Checkpoint 1 → 5.

Nộp theo [`SUBMISSION.md`](SUBMISSION.md) · Quy định: [`RULES.md`](RULES.md).
