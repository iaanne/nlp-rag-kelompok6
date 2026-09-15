---
license: cc0-1.0
datasets:
- Paxrad/EWS_v5_USONLY_final
tags:
- military-medicine
- emergency-care
- qa-pairs
- open-source
- medical
language:
- en
task_categories:
- question-answering
pretty_name: Emergency War Surgery QA Dataset
---

# Emergency War Surgery QA Dataset (v5)

This dataset contains 86 high-quality, open-ended question–answer pairs generated from the U.S. Department of Defense’s *Emergency War Surgery* (EWS) manual. The content is extracted, chunked, and QA-labeled for use in sovereign AI systems, medical QA fine-tuning, or local RAG pipelines.

## Contents

- **Source**: Emergency War Surgery (public domain)
- **Chunks**: 450-token segments with overlap
- **QA Pairs**: 1–2 generated per chunk, validated and filtered
- **Format**: JSONL
- **License**: Public Domain (U.S. Federal Work)

## Example Format

```json
{"id": "EWS.v5.QA0004_0", "chunk_id": "EWS.v5.CHUNK0004", "question": "What unique medical challenges do military surgeons face that are not typically found in civilian settings?", "answer": "Military surgeons face unique medical challenges such as blast wounds, burns, multiple penetrating injuries, head trauma, hemorrhage control, and amputations.", "question_type": "open-ended", "license": "PUBLIC_DOMAIN"}