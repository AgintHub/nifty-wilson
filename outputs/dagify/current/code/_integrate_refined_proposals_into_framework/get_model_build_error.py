# -- PRD --
# 1. BULLET: Implement a function to extract the error message from the model building
#   process. This may involve parsing the error message and returning a user-
#   friendly string.
#   Reason: We need to provide a way to extract the error message to diagnose and fix
#           the issue.
#   Impact: This will improve the debugging experience and reduce the time it takes to
#           diagnose model building issues.
#   Complexity: LOW
#   Method: Utilize a library like `traceback` to extract the error message and then
#           parse it to return a user-friendly string.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Integrate the error extraction function into the model building process. This
#   may involve modifying existing code or adding new calls to the extraction
#   function.
#   Reason: We need to integrate the error extraction functionality into the existing
#           model building process to make it useful.
#   Impact: This will improve the overall model building experience by providing better
#           error handling and diagnosis.
#   Complexity: MEDIUM
#   Method: Modify the model building code to call the error extraction function and
#           handle the returned output.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Test the integrated error extraction functionality to ensure it works as
#   expected. This may involve writing test cases to cover different error
#   scenarios.
#   Reason: We need to test the integrated functionality to catch any issues and ensure
#           it works as expected.
#   Impact: This will improve the overall quality of the model building process and
#           reduce the number of bugs.
#   Complexity: MEDIUM
#   Method: Write test cases using a library like `unittest` to cover different error
#           scenarios and verify the expected output.
# -- END PRD --


def get_model_build_error(equation: str) -> str:
    """
    Extracts the error message that occurs during model building.

    Args:
        equation: Input parameter of type str

    Returns:
        str: Output of type str
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
