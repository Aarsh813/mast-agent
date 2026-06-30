import json
from mast_agent.diagnosis.prompts import DIAGNOSIS_SYSTEM_PROMPT, DIAGNOSIS_USER_PROMPT, DiagnosisOutput
from mast_agent.diagnosis.llm_factory import LLMFactory
from langchain_core.messages import SystemMessage, HumanMessage

class MASTClassifier:
    def __init__(self, provider: str = None, model: str = None):
        import os
        provider = provider or os.getenv("MAST_LLM_PROVIDER", "groq")
        model = model or os.getenv("MAST_LLM_MODEL", "llama-3.1-70b-versatile")
        self.llm = LLMFactory.create(provider, model)

    def _format_trace(self, trace_spans: list) -> str:
        lines = []
        for span in trace_spans:
            role = span.agent_role or "unknown"
            typ = span.span_type
            if typ == "llm_call":
                lines.append(f"[{span.id}] {role} (LLM Call): {span.output_content}")
            elif typ == "agent_message":
                lines.append(f"[{span.id}] {role} sent message: {span.input_content}")
        return "\n".join(lines)

    async def diagnose(self, run_id: str, trace_spans: list, task: str, outcome: str) -> dict:
        formatted = self._format_trace(trace_spans)
        
        sys_msg = SystemMessage(content=DIAGNOSIS_SYSTEM_PROMPT)
        user_msg = HumanMessage(content=DIAGNOSIS_USER_PROMPT.format(
            run_id=run_id,
            formatted_trace=formatted,
            outcome=outcome,
            task=task
        ))
        
        llm_with_struct = self.llm.with_structured_output(DiagnosisOutput)
        response: DiagnosisOutput = llm_with_struct.invoke([sys_msg, user_msg])
        
        return response.dict()
