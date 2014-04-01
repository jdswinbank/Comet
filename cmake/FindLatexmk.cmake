find_program(LATEXMK_EXECUTABLE
    NAMES "latexmk"
)

include (FindPackageHandleStandardArgs)
find_package_handle_standard_args (Latexmk
    DEFAULT_MSG
    LATEXMK_EXECUTABLE
)

