import google.generativeai as genai
from app.core.config import settings


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def generate_text(self, prompt: str, temperature: float = 0.1) -> str:
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,
            )
        )
        return response.text
    
    async def analyze_with_context(self, query: str, context: str) -> str:
        prompt = f"""Context:
{context}

Query:
{query}

Based on the context provided, answer the query in detail."""
        
        return await self.generate_text(prompt)


gemini_service = GeminiService()
