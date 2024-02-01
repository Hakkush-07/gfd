class FigureException(Exception):
    """
    errors in the figure, construction functions etc.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class GFDException(Exception):
    """
    errors in the gfd file
    """
    def __init__(self, message, input_file=None, line_count=None):
        self.message = message
        self.line_count = line_count
        self.input_file = input_file
        info = f"Error in line {self.line_count} of {self.input_file}: " if self.line_count else ""
        super().__init__(info + self.message)
