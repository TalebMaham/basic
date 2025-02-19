import unittest
from app import app

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        """Initialisation du client de test"""
        self.app = app.test_client()

    def test_hello(self):
        """Test de la route '/'"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Hello, World!")

    def test_test1(self):
        """Test de la route '/test1'"""
        response = self.app.get('/test1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Test 1 Passed")

    def test_test2(self):
        """Test de la route '/test2'"""
        response = self.app.get('/test2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Test 2 Passed")

if __name__ == '__main__':
    unittest.main()
