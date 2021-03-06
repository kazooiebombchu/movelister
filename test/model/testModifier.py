from movelister.model.modifier import Modifier
import unittest


class ModifierTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.modifier1 = Modifier('aaa')
        self.modifier2 = Modifier('aaa')
        self.modifier3 = Modifier('bbb')

    def testEquality(self):
        self.assertTrue(self.modifier1 == self.modifier2)
        self.assertFalse(self.modifier1 == self.modifier3)

    def testNonequality(self):
        self.assertTrue(self.modifier1 != self.modifier3)
        self.assertFalse(self.modifier1 != self.modifier2)
