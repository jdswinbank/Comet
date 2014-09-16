find_program(PYGMENTIZE_EXECUTABLE
    NAMES "pygmentize"
)

include (FindPackageHandleStandardArgs)
find_package_handle_standard_args (Pygments
    DEFAULT_MSG
    PYGMENTIZE_EXECUTABLE
)

