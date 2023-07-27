import sys
import traceback


class AssertionHandler:

    @staticmethod
    def testAssertion(assertion:bool):
        try:
            assert assertion
        except AssertionError as e:
            traceback.print_stack()
            sys.exit(f"Assertion Failed!")

