import unittest
import striphtml

class TestStringStripHtmlTransform(unittest.TestCase):
    def test_striphtml(self):
        transformer = striphtml.StringStripHtmlTransform()
        self.assertEqual(transformer.transform(''), '')
        self.assertEqual(transformer.transform('<b>Bold</b>'), 'Bold')
        self.assertEqual(transformer.transform('< 3 donuts and > 4 pies'), '< 3 donuts and > 4 pies')
        self.assertEqual(transformer.transform('4 is &lt; 5'), u'4 is < 5')
