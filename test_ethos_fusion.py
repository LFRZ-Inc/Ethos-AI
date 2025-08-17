#!/usr/bin/env python3
"""
Test Script for Ethos Fusion Engine - The "Frankenstein AI"
Demonstrates how multiple models combine into one unified Ethos AI
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ethos_fusion_engine import EthosFusionEngine

async def test_ethos_fusion():
    """
    Test the Ethos Fusion Engine with different types of queries
    """
    print("🧠 Ethos Fusion Engine - The 'Frankenstein AI' Test")
    print("=" * 60)
    
    # Initialize the fusion engine
    fusion_engine = EthosFusionEngine()
    
    # Test queries
    test_queries = [
        {
            "type": "Programming",
            "query": "Write a Python function to calculate fibonacci numbers with error handling"
        },
        {
            "type": "Analysis", 
            "query": "Analyze the benefits and drawbacks of using local AI models vs cloud AI services"
        },
        {
            "type": "Creative",
            "query": "Write a short story about a robot learning to understand human emotions"
        },
        {
            "type": "General",
            "query": "What are the key principles of machine learning and how do they apply to AI development?"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🔬 Test {i}: {test_case['type']} Query")
        print("-" * 40)
        print(f"Query: {test_case['query']}")
        print("\n🤖 Generating unified Ethos response...")
        
        try:
            # Generate unified response
            ethos_response = await fusion_engine.generate_unified_response(test_case['query'])
            
            print(f"\n✅ Ethos AI Response:")
            print(f"Confidence: {ethos_response.confidence:.2f}")
            print(f"Models Used: {', '.join(ethos_response.source_models)}")
            print(f"Capabilities: {', '.join(ethos_response.capabilities_used)}")
            print(f"\n📝 Response:")
            print(ethos_response.final_response)
            
            print(f"\n🧠 Synthesis Reasoning:")
            print(ethos_response.reasoning)
            
            print(f"\n📊 Learning Insights:")
            insights = ethos_response.learning_insights
            print(f"- Models: {insights['models_used']}")
            print(f"- Avg Response Time: {insights['performance_metrics']['avg_response_time']:.2f}s")
            print(f"- Model Diversity: {insights['performance_metrics']['model_diversity']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)
    
    # Show learning summary
    print("\n📈 Learning Summary:")
    print("-" * 40)
    learning_summary = fusion_engine.get_learning_summary()
    print(f"Total Interactions: {learning_summary['total_interactions']}")
    print(f"Performance Trend: {learning_summary['performance_trends']['trend']}")
    print(f"Capabilities Used: {len(learning_summary['capability_insights'])}")
    
    print("\n🎯 Response Patterns:")
    for pattern, entries in learning_summary['response_patterns'].items():
        print(f"- {pattern}: {len(entries)} interactions")
    
    print("\n🚀 Ethos Fusion Engine Test Complete!")
    print("This demonstrates how multiple models combine into one unified Ethos AI!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_ethos_fusion())
