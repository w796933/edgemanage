#!/usr/bin/env python

import unittest
import tempfile

import edgestate

TEST_EDGE = "testedge1"
TEST_FETCH_HISTORY = 4
# Patch edgestate's import of const
edgestate.FETCH_HISTORY = TEST_FETCH_HISTORY

class EdgeStateTest(unittest.TestCase):

    # TODO load test JSON file to ensure object creation

    def testStoreAverage(self):
        store_dir = tempfile.mkdtemp()
        a = edgestate.EdgeState(TEST_EDGE, store_dir)

        for i in range(4):
            a.add_value(2)

        average = a.current_average()
        self.assertEqual(average, 2)

    def testStoreRotation(self):
        store_dir = tempfile.mkdtemp()
        a = edgestate.EdgeState(TEST_EDGE, store_dir)

        for i in range(5):
            a.add_value(2)

        self.assertEqual(len(a), TEST_FETCH_HISTORY)

if __name__ == '__main__':
    unittest.main()