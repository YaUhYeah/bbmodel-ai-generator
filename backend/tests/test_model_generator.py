import unittest
import json
import os
from app.services.model_generator import ModelGenerator

class TestModelGenerator(unittest.TestCase):
    def setUp(self):
        self.model_generator = ModelGenerator()
        self.test_prompt = "A blocky robot character with red armor"
        self.test_model_id = "test_model_id"
        self.test_user_id = "test_user_id"
    
    def test_generate_mock_bbmodel(self):
        # Test character model generation
        character_model = self.model_generator._generate_mock_bbmodel(
            prompt=self.test_prompt,
            model_type="character",
            animation_type=None,
            user_id=self.test_user_id
        )
        
        # Check basic structure
        self.assertIn("meta", character_model)
        self.assertIn("elements", character_model)
        self.assertIn("animations", character_model)
        self.assertIn("metadata", character_model)
        
        # Check metadata
        self.assertEqual(character_model["metadata"]["prompt"], self.test_prompt)
        self.assertEqual(character_model["metadata"]["model_type"], "character")
        self.assertEqual(character_model["metadata"]["user_id"], self.test_user_id)
        
        # Check elements for character model
        self.assertTrue(len(character_model["elements"]) >= 6)  # Head, body, arms, legs
        
        # Test animal model generation
        animal_model = self.model_generator._generate_mock_bbmodel(
            prompt=self.test_prompt,
            model_type="animal",
            animation_type=None,
            user_id=self.test_user_id
        )
        
        # Check elements for animal model
        self.assertTrue(len(animal_model["elements"]) >= 5)  # Body, head, legs, tail
    
    def test_generate_animations(self):
        # Generate a character model
        elements = self.model_generator._generate_character_elements()
        
        # Test walk animation
        walk_animation = self.model_generator._generate_walk_animation(elements)
        self.assertEqual(walk_animation["name"], "walk")
        self.assertEqual(walk_animation["loop"], "loop")
        
        # Test idle animation
        idle_animation = self.model_generator._generate_idle_animation(elements)
        self.assertEqual(idle_animation["name"], "idle")
        self.assertEqual(idle_animation["loop"], "loop")
        
        # Test attack animation
        attack_animation = self.model_generator._generate_attack_animation(elements)
        self.assertEqual(attack_animation["name"], "attack")
        self.assertEqual(attack_animation["loop"], "once")

if __name__ == "__main__":
    unittest.main()