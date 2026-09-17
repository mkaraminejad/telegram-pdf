"""Test Suite Runner for Persian PDF to DOCX Bot.

Runs all unit and integration tests and outputs structured results.
Can be executed with standard python3: `python3 -m bot.tests.run_tests`
"""
import unittest
import sys
import os

# Add root directory to python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from bot.tests.test_normalizer import TestPersianNormalizer


def run_all_tests():
    print("=" * 70)
    print("🚀 Running Persian PDF to DOCX Bot Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Always add pure Python unit tests
    suite.addTests(loader.loadTestsFromTestCase(TestPersianNormalizer))

    # Try adding docx tests if python-docx is installed
    try:
        from bot.tests.test_docx_rtl import TestDocxRTL
        suite.addTests(loader.loadTestsFromTestCase(TestDocxRTL))
        print("✅ Added DOCX RTL & OpenXML Unit Tests")
    except ImportError as e:
        print(f"ℹ️ Skipping Docx tests in minimal environment: {e}")

    # Try adding integration tests if PyMuPDF is installed
    try:
        from bot.tests.test_integration import TestPDFIntegration
        suite.addTests(loader.loadTestsFromTestCase(TestPDFIntegration))
        print("✅ Added PDF Pipeline Integration Tests")
    except ImportError as e:
        print(f"ℹ️ Skipping Integration tests in minimal environment: {e}")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"🎉 ALL TESTS PASSED! ({result.testsRun} tests executed successfully)")
        print("=" * 70)
        return 0
    else:
        print(f"❌ SOME TESTS FAILED! (Failures: {len(result.failures)}, Errors: {len(result.errors)})")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
