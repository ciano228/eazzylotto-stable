import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class LLMProviderService:
    """
    Unified LLM Provider Service.
    All providers return a NORMALIZED response:
        {'status': 'success', 'provider': '...', 'text': '...'}
    or  {'status': 'error', 'error': '...'}
    """

    def __init__(self):
        load_dotenv(override=True)
        self.api_keys = {
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'mistral': os.getenv('MISTRAL_API_KEY'),
            'deepseek': os.getenv('DEEPSEEK_API_KEY'),
            'groq': os.getenv('GROQ_API_KEY'),
            'ollama': None
        }

    def generate_text(self, provider: str, model: str, message: str, **kwargs) -> Dict[str, Any]:
        provider = provider.lower()
        api_key = kwargs.get('api_key') or self.api_keys.get(provider)

        if provider != 'ollama' and not api_key:
            return {'status': 'error', 'error': f'No API key configured for {provider}. Add it to .env'}

        try:
            if provider == 'anthropic' or provider == 'claude':
                return self._call_anthropic(api_key, model, message, **kwargs)
            elif provider == 'openai':
                return self._call_openai(api_key, model, message, **kwargs)
            elif provider == 'deepseek':
                return self._call_deepseek(api_key, model, message, **kwargs)
            elif provider == 'mistral':
                return self._call_mistral(api_key, model, message, **kwargs)
            elif provider == 'groq':
                return self._call_groq(api_key, model, message, **kwargs)
            elif provider == 'ollama':
                return self._call_ollama(model, message, **kwargs)
            else:
                return {'status': 'error', 'error': f'Unknown provider: {provider}'}
        except requests.exceptions.ConnectionError as e:
            return {'status': 'error', 'error': f'Connection refused for {provider}. Is the service running?'}
        except requests.exceptions.Timeout:
            return {'status': 'error', 'error': f'{provider} API timed out after 30s'}
        except Exception as e:
            return {'status': 'error', 'error': f'{provider} error: {str(e)}'}

    # --- Helper to parse OpenAI-compatible responses ---
    def _parse_openai_response(self, resp, provider_name):
        """Parse response from OpenAI-compatible APIs (OpenAI, DeepSeek, Groq, Mistral)."""
        if not resp.ok:
            return {'status': 'error', 'error': f'{provider_name} API Error {resp.status_code}: {resp.text[:200]}'}

        data = resp.json()

        # Check for API-level error
        if 'error' in data:
            return {'status': 'error', 'error': f"{provider_name}: {data['error'].get('message', str(data['error']))}"}

        # Extract text from choices
        try:
            text = data['choices'][0]['message']['content']
            return {'status': 'success', 'provider': provider_name, 'text': text}
        except (KeyError, IndexError) as e:
            return {'status': 'error', 'error': f'{provider_name} unexpected response format: {str(data)[:200]}'}

    # --- Anthropic (Messages API v1) ---
    def _call_anthropic(self, api_key, model, message, **kwargs):
        url = 'https://api.anthropic.com/v1/messages'
        system_prompt = kwargs.get('system_prompt', 'You are a helpful assistant.')
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
        payload = {
            'model': model or 'claude-3-5-sonnet-20241022',
            'max_tokens': int(kwargs.get('max_tokens', 512)),
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': message}]
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)

        if not resp.ok:
            return {'status': 'error', 'error': f'Anthropic API Error {resp.status_code}: {resp.text[:200]}'}

        data = resp.json()
        try:
            text = data['content'][0]['text']
            return {'status': 'success', 'provider': 'anthropic', 'text': text}
        except (KeyError, IndexError):
            return {'status': 'error', 'error': f'Anthropic unexpected response: {str(data)[:200]}'}

    # --- OpenAI ---
    def _call_openai(self, api_key, model, message, **kwargs):
        url = os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions')
        system_prompt = kwargs.get('system_prompt', 'You are a helpful assistant.')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        payload = {
            'model': model or 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': int(kwargs.get('max_tokens', 512)),
            'temperature': float(kwargs.get('temperature', 0.7))
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        return self._parse_openai_response(resp, 'openai')

    # --- DeepSeek (OpenAI-compatible) ---
    def _call_deepseek(self, api_key, model, message, **kwargs):
        url = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/chat/completions')
        system_prompt = kwargs.get('system_prompt', 'You are a helpful assistant.')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        payload = {
            'model': model or 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            'stream': False
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        return self._parse_openai_response(resp, 'deepseek')

    # --- Mistral (OpenAI-compatible) ---
    def _call_mistral(self, api_key, model, message, **kwargs):
        url = os.getenv('MISTRAL_API_URL', 'https://api.mistral.ai/v1/chat/completions')
        system_prompt = kwargs.get('system_prompt', 'You are a helpful assistant.')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        payload = {
            'model': model or 'mistral-small-latest',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        return self._parse_openai_response(resp, 'mistral')

    # --- Groq (OpenAI-compatible, FREE tier) ---
    def _call_groq(self, api_key, model, message, **kwargs):
        url = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
        system_prompt = kwargs.get('system_prompt', 'You are a helpful assistant.')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        payload = {
            'model': model or 'mixtral-8x7b-32768',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': int(kwargs.get('max_tokens', 512))
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        return self._parse_openai_response(resp, 'groq')

    # --- Ollama (Local, FREE) ---
    def _call_ollama(self, model, message, **kwargs):
        url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
        system_prompt = kwargs.get('system_prompt', 'You are a helpful assistant.')
        payload = {
            'model': model or 'mistral',
            'prompt': message,
            'system': system_prompt,
            'stream': False
        }
        resp = requests.post(url, json=payload, timeout=60)

        if not resp.ok:
            return {'status': 'error', 'error': f'Ollama Error {resp.status_code}: {resp.text[:200]}'}

        data = resp.json()
        text = data.get('response', '')
        if not text:
            return {'status': 'error', 'error': f'Ollama returned empty response. Is model "{model}" pulled?'}
        return {'status': 'success', 'provider': 'ollama', 'text': text}
