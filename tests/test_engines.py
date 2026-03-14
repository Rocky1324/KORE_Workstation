import unittest
import sys
import os

# Adjust path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.lab_engine import LabEngine
from core.graph_engine import GraphEngine

class TestKoreEngines(unittest.TestCase):
    
    def setUp(self):
        self.lab_engine = LabEngine()
        self.graph_engine = GraphEngine()
        
    def test_lab_engine_initialization(self):
        """Verify LabEngine components are present."""
        self.assertIsNotNone(self.lab_engine)
        # Check for DC Solver constants or methods
        self.assertTrue(hasattr(self.lab_engine, 'solve_circuit'))
        
    def test_graph_engine_extraction(self):
        """Verify GraphEngine can extract tags from text."""
        test_text = "Ceci est un test avec #thermo et #physique."
        tags = self.graph_engine.extract_tags(test_text)
        self.assertIn("#thermo", tags)
        self.assertIn("#physique", tags)
        self.assertEqual(len(tags), 2)

    def test_graph_build_structure(self):
        """Verify graph data structure format."""
        # This might return empty if DB is empty, but we check keys
        data = self.graph_engine.build_graph_data()
        self.assertIn('nodes', data)
        self.assertIn('edges', data)

if __name__ == '__main__':
    unittest.main()
