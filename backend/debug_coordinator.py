import asyncio
from app.services.coordinator import AnalysisCoordinator

SAMPLE_CHAT_TEXT = """
01/01/2026, 12:00 - Alice: Hey!
01/01/2026, 12:01 - Bob: Hi there. How's it going?
01/01/2026, 12:02 - Alice: Great, just working on this new AI app.
01/01/2026, 12:03 - Bob: Nice. k.
"""

async def main():
    coordinator = AnalysisCoordinator()
    print("Running analysis...")
    try:
        result = await coordinator.run_full_analysis(SAMPLE_CHAT_TEXT)
        print("Success!")
        print(f"Summary: {result.overall_summary}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
