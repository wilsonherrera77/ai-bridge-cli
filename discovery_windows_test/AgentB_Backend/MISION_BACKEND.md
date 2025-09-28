# AGENTE BACKEND - MOTOR DE DESCUBRIMIENTO

## TU MISIÓN
Implementar motor de crawling y providers para descubrimiento exhaustivo.

## ARCHIVOS A CREAR EN ESTE DIRECTORIO:

### 1. discovery_engine.py (Principal)
```python
#!/usr/bin/env python3
import asyncio
import aiohttp
from typing import List, Dict, Any
from providers.web_provider import WebProvider
from providers.reddit_provider import RedditProvider
from providers.youtube_provider import YouTubeProvider
from extraction import ContentExtractor
from deduplication import Deduplicator
from scoring import ContentScorer

class DiscoveryEngine:
    def __init__(self):
        self.providers = {
            'web': WebProvider(),
            'reddit': RedditProvider(),
            'youtube': YouTubeProvider()
        }
        self.extractor = ContentExtractor()
        self.deduplicator = Deduplicator()
        self.scorer = ContentScorer()
    
    async def discover_content(self, topic_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Motor principal de descubrimiento"""
        print(f"🔍 Descubriendo: {topic_config['topic']}")
        
        all_results = []
        
        # Ejecutar providers en paralelo
        tasks = []
        for platform in topic_config['platform']:
            if platform in self.providers:
                task = self.providers[platform].search(
                    query=topic_config['query'] or topic_config['topic'],
                    config=topic_config
                )
                tasks.append(task)
        
        # Recopilar resultados
        if tasks:
            provider_results = await asyncio.gather(*tasks, return_exceptions=True)
            for results in provider_results:
                if isinstance(results, list):
                    all_results.extend(results)
        
        # Procesar resultados
        processed_results = []
        for result in all_results:
            # Extraer contenido completo
            extracted = await self.extractor.extract_content(result)
            if extracted:
                processed_results.append(extracted)
        
        # Deduplicar
        unique_results = self.deduplicator.remove_duplicates(processed_results)
        
        # Calcular scores
        scored_results = []
        for result in unique_results:
            score = self.scorer.calculate_score(result, topic_config)
            result['relevance_score'] = score
            scored_results.append(result)
        
        # Ordenar por relevancia
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Limitar resultados
        max_per_topic = topic_config.get('max_per_topic', 100)
        return scored_results[:max_per_topic]

if __name__ == "__main__":
    # Prueba básica
    engine = DiscoveryEngine()
    test_config = {
        'topic': 'Inteligencia Artificial',
        'query': 'AI machine learning 2024',
        'platform': ['web'],
        'depth': 2,
        'max_per_topic': 10
    }
    
    async def test():
        results = await engine.discover_content(test_config)
        print(f"Encontrados: {len(results)} resultados")
    
    asyncio.run(test())
```

### 2. providers/web_provider.py
```python
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import random

class WebProvider:
    def __init__(self):
        self.name = "web"
        self.session = None
    
    async def search(self, query: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Buscar en web general"""
        print(f"🌐 WebProvider buscando: {query}")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        results = []
        
        try:
            # Simular búsqueda web (en producción usar API real)
            await asyncio.sleep(random.uniform(1, 3))  # Simular latencia
            
            # Resultados simulados realistas
            sample_results = [
                {
                    "title": f"Advanced {query} Research 2024",
                    "url": f"https://research.example.com/{query.replace(' ', '-').lower()}",
                    "domain": "research.example.com",
                    "snippet": f"Latest developments in {query} showing promising results...",
                    "source_type": "web"
                },
                {
                    "title": f"{query} Implementation Guide",
                    "url": f"https://tech.example.org/guides/{query.replace(' ', '-').lower()}",
                    "domain": "tech.example.org", 
                    "snippet": f"Comprehensive guide for implementing {query} solutions...",
                    "source_type": "web"
                },
                {
                    "title": f"Industry Report: {query} Trends",
                    "url": f"https://industry.example.net/reports/{query.replace(' ', '-').lower()}",
                    "domain": "industry.example.net",
                    "snippet": f"Annual industry analysis of {query} market trends...",
                    "source_type": "web"
                }
            ]
            
            # Simular crawling más allá de semillas
            seed_url = config.get('seed_url', '')
            if seed_url:
                # Agregar resultados relacionados con la semilla
                sample_results.append({
                    "title": f"Related Content from {seed_url}",
                    "url": f"{seed_url}/related/{query.replace(' ', '-').lower()}",
                    "domain": seed_url.replace('https://', '').replace('http://', '').split('/')[0],
                    "snippet": f"Content discovered from seed URL related to {query}...",
                    "source_type": "web"
                })
            
            results.extend(sample_results[:config.get('depth', 3)])
            
        except Exception as e:
            print(f"❌ Error en WebProvider: {e}")
        
        return results
    
    async def close(self):
        if self.session:
            await self.session.close()
```

### 3. extraction.py
```python
import aiohttp
import trafilatura
from datetime import datetime
from typing import Dict, Any, Optional

class ContentExtractor:
    def __init__(self):
        self.session = None
    
    async def extract_content(self, raw_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extraer contenido completo de URL"""
        try:
            url = raw_result.get('url', '')
            if not url:
                return None
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Descargar contenido
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
            
            # Extraer con trafilatura
            extracted_text = trafilatura.extract(html)
            if not extracted_text:
                extracted_text = raw_result.get('snippet', '')
            
            # Extraer metadatos
            metadata = trafilatura.extract_metadata(html)
            
            # Estructurar resultado
            result = {
                "title": raw_result.get('title', metadata.title if metadata else ''),
                "text": extracted_text,
                "author": metadata.author if metadata else '',
                "published_at": metadata.date if metadata else datetime.now().isoformat(),
                "domain": raw_result.get('domain', ''),
                "url": url,
                "source_type": raw_result.get('source_type', 'web'),
                "snippet": raw_result.get('snippet', '')
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error extrayendo {raw_result.get('url', '')}: {e}")
            return None
    
    async def close(self):
        if self.session:
            await self.session.close()
```

### 4. deduplication.py
```python
import hashlib
from typing import List, Dict, Any, Set
from fuzzywuzzy import fuzz

class Deduplicator:
    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.seen_urls: Set[str] = set()
    
    def content_hash(self, text: str) -> str:
        """Generar hash del contenido"""
        # Normalizar texto
        normalized = text.lower().strip()
        normalized = ''.join(normalized.split())  # Remover espacios
        
        # Generar hash
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Eliminar duplicados por contenido y URL"""
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            text = result.get('text', '')
            
            # Check URL duplicado
            if url in self.seen_urls:
                continue
            
            # Check contenido duplicado
            content_hash = self.content_hash(text)
            if content_hash in self.seen_hashes:
                continue
            
            # Check similarity con resultados existentes
            is_similar = False
            for existing in unique_results:
                existing_text = existing.get('text', '')
                similarity = fuzz.ratio(text, existing_text)
                if similarity > 85:  # 85% similarity threshold
                    is_similar = True
                    break
            
            if not is_similar:
                self.seen_urls.add(url)
                self.seen_hashes.add(content_hash)
                unique_results.append(result)
        
        print(f"🧹 Deduplicación: {len(results)} -> {len(unique_results)} únicos")
        return unique_results
```

### 5. scoring.py
```python
from datetime import datetime, timezone
from typing import Dict, Any
import re
from fuzzywuzzy import fuzz

class ContentScorer:
    def calculate_score(self, result: Dict[str, Any], topic_config: Dict[str, Any]) -> float:
        """Calcular score por relevancia/recencia/diversidad"""
        
        # Relevancia (40% del score)
        relevance_score = self._calculate_relevance(result, topic_config)
        
        # Recencia (35% del score)
        recency_score = self._calculate_recency(result, topic_config)
        
        # Diversidad (25% del score)
        diversity_score = self._calculate_diversity(result)
        
        # Score total ponderado
        total_score = (relevance_score * 0.4) + (recency_score * 0.35) + (diversity_score * 0.25)
        
        return round(total_score, 3)
    
    def _calculate_relevance(self, result: Dict[str, Any], topic_config: Dict[str, Any]) -> float:
        """Calcular relevancia con el topic/query"""
        query = topic_config.get('query', topic_config.get('topic', ''))
        title = result.get('title', '')
        text = result.get('text', '')
        
        # Similarity con título (peso mayor)
        title_score = fuzz.partial_ratio(query.lower(), title.lower()) / 100
        
        # Similarity con texto (peso menor)
        text_score = fuzz.partial_ratio(query.lower(), text[:500].lower()) / 100
        
        # Score combinado
        relevance = (title_score * 0.7) + (text_score * 0.3)
        
        return relevance
    
    def _calculate_recency(self, result: Dict[str, Any], topic_config: Dict[str, Any]) -> float:
        """Calcular score de recencia"""
        try:
            published_str = result.get('published_at', '')
            if not published_str:
                return 0.5  # Score neutral si no hay fecha
            
            # Parse fecha
            if 'T' in published_str:
                published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            else:
                published_date = datetime.fromisoformat(published_str)
            
            # Calcular días desde publicación
            now = datetime.now(timezone.utc)
            if published_date.tzinfo is None:
                published_date = published_date.replace(tzinfo=timezone.utc)
            
            days_old = (now - published_date).days
            
            # Score basado en recency_days configurado
            max_days = topic_config.get('recency_days', 30)
            
            if days_old <= max_days:
                # Score alto para contenido reciente
                recency_score = 1.0 - (days_old / max_days * 0.5)
            else:
                # Score bajo para contenido viejo
                recency_score = 0.5 * (1 / (1 + (days_old - max_days) / max_days))
            
            return max(0.1, recency_score)  # Mínimo 0.1
            
        except Exception:
            return 0.5  # Score neutral si hay error
    
    def _calculate_diversity(self, result: Dict[str, Any]) -> float:
        """Calcular score de diversidad (dominio/fuente)"""
        domain = result.get('domain', '')
        source_type = result.get('source_type', '')
        
        # Bonus por diferentes tipos de fuente
        source_bonus = {
            'web': 0.8,
            'reddit': 0.9,
            'youtube': 0.95,
            'twitter': 0.85,
            'rss': 0.7
        }
        
        base_score = source_bonus.get(source_type, 0.5)
        
        # Bonus por dominios menos comunes (simulado)
        common_domains = ['google.com', 'wikipedia.org', 'youtube.com']
        if domain not in common_domains:
            base_score += 0.2
        
        return min(1.0, base_score)
```

## COORDINACIÓN CON FRONTEND
Expón esta API para el frontend:
```python
from discovery_engine import DiscoveryEngine

engine = DiscoveryEngine()
results = await engine.discover_content(topic_config)
```

## SIGUIENTE PASO
1. Implementa discovery_engine.py como motor principal
2. Crea providers/web_provider.py funcional
3. Implementa extraction.py con trafilatura
4. Crea deduplication.py robusto
5. Implementa scoring.py con métricas reales
6. Agrega más providers (Reddit, YouTube, RSS)

IMPORTANTE: El motor debe descubrir contenido MÁS ALLÁ de las semillas iniciales.
