# Field guide: AI / ML / LLM / agent roles

The most competitive and fastest-moving segment of 2026 hiring — and
the one where generic resumes die fastest, because every applicant
lists the same frameworks. What differentiates is *evidence of the
work the role actually consists of*.

## What counts as evidence (strongest first)

1. **Evals.** Built an evaluation harness, defined metrics, caught
   regressions, ran A/Bs on model behavior. In 2026 eval literacy is
   the single most-screened-for practical skill in LLM engineering
   roles; a concrete eval bullet outweighs a framework list.
2. **Agents / tool use.** Built agent systems: tool definitions,
   orchestration, failure handling, guardrails, memory. Name what the
   agent did and its reliability numbers, not the word "agentic".
3. **RAG / retrieval.** Pipelines with measured quality (recall@k,
   latency, answer accuracy) — the measurement is the evidence.
4. **Training / fine-tuning.** Dataset size, base model, method (LoRA,
   DPO, RLHF-adjacent), and the before→after metric on a held-out set.
   "Fine-tuned Whisper-small on 30 h, WER 18.2%→11.6%" is a hire
   signal; "experience with fine-tuning" is nothing.
5. **Research artifacts.** Papers (venue + author position), preprints,
   workshop posters, reproductions of published results ("reproduced 3
   baselines within 2%" is respected — it's most of real ML work).
6. **Open source.** PRs merged into known repos > personal repos with
   stars > personal repos without. Link everything.
7. **Infrastructure.** GPU scheduling, inference serving, quantization,
   data pipelines — systems evidence transfers fully into ML roles.

## Vocabulary norms

- Name models, methods, and metrics precisely (p95, recall@10, WER,
  pass@1, MMLU-style evals). Precision reads as fluency; the semantic
  matcher rewards the real terms the JD uses.
- Avoid hype tokens: "GenAI", "cutting-edge AI", "AI-powered" (as
  self-description), "prompt wizard". The people screening build these
  systems; hype reads as outsider.
- "LLM" not "large language models (LLMs)" on every use — once
  expanded, then the acronym.

## Red flags screeners notice

- A skills section listing every framework that has ever existed
  (instant keyword-stuffing prior).
- Course projects presented as production systems (say "course
  project" — honesty here is cheap, discovery is expensive).
- Percentages on model metrics with no dataset/baseline context.
- "Prompt engineering" as the only LLM evidence for an engineering
  role — pair it with evals, integration, or data work.

## Entry ordering for this field

Students/new grads: Education → Experience → Projects → Skills →
Publications (if any) → Awards. Research-track (PhD-adjacent) profiles:
Education → Publications → Research Experience → Projects → Skills.
Industry-track with internships: Experience before Projects.

## Degree/coursework conventions

- GPA: include if ≥ 3.7 (US) or equivalent; otherwise omit silently.
- Coursework: max one line, only field-relevant, hardest first (e.g.
  "Machine Learning, Convex Optimization, Distributed Systems").
- MOOCs/certificates: omit for degree-holders unless from a recognized
  program AND backed by a project bullet somewhere.
