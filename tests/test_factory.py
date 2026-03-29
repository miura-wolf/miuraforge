import unittest
from llm.factory import LLMFactory
from llm.providers import ResilientProvider, NvidiaProvider, GeminiProvider

class TestLLMFactory(unittest.TestCase):

    def test_factory_research(self):
        brain = LLMFactory.get_brain("research")
        self.assertIsInstance(brain, ResilientProvider)
        # DeepSeek V3.2 debe ser el primer tier
        self.assertEqual(brain.tiers[0].model, "deepseek-ai/deepseek-v3.2")

    def test_factory_merch(self):
        brain = LLMFactory.get_brain("merch")
        self.assertIsInstance(brain, ResilientProvider)
        # Gemma 3 debe estar en los tiers
        self.assertEqual(brain.tiers[0].model, "google/gemma-3-27b-it")

    def test_factory_visual(self):
        brain = LLMFactory.get_brain("visual")
        self.assertIsInstance(brain, ResilientProvider)
        self.assertEqual(brain.tiers[0].model, "meta/llama-3.2-11b-vision-instruct")

if __name__ == '__main__':
    unittest.main()
