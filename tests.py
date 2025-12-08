import unittest
from datetime import timedelta
from logic.procesador import _format_time, _esc

class TestFuncional(unittest.TestCase):
    
    def test_escape_string(self):
        """Prueba función pura de escape de caracteres"""
        self.assertEqual(_esc("O'Connor"), "O\\'Connor")
        self.assertEqual(_esc("Juan"), "Juan")

    def test_format_timedelta(self):
        """Prueba formateo de timedelta (Paradigma Funcional)"""
        td = timedelta(hours=9, minutes=30)
        self.assertEqual(_format_time(td), "09:30")
        
    def test_format_string(self):
        """Prueba fallback de string"""
        self.assertEqual(_format_time("10:00:00"), "10:00")

if __name__ == '__main__':
    unittest.main()