project (comet-paper)
cmake_minimum_required (VERSION 2.8)

set (CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")

find_package (LATEX REQUIRED)
find_package (LATEXMK REQUIRED)
find_package (PYTHONINTERP REQUIRED)

set (FIGURE_OUTPUT_DIR ${PROJECT_BINARY_DIR}/figures/)

configure_file (
    ${PROJECT_SOURCE_DIR}/manuscript/comet.tex
    ${PROJECT_BINARY_DIR}/comet.tex
    @ONLY
)

configure_file (
    ${PROJECT_SOURCE_DIR}/manuscript/comet.bib
    ${PROJECT_BINARY_DIR}/comet.bib
    @ONLY
)

configure_file (
    ${PROJECT_SOURCE_DIR}/manuscript/vtp.pdf
    ${FIGURE_OUTPUT_DIR}/vtp.pdf
    COPYONLY
)

add_custom_command (
    OUTPUT ${FIGURE_OUTPUT_DIR}/latency.pdf
    COMMAND ${PYTHON_EXECUTABLE}
    ARGS ${PROJECT_SOURCE_DIR}/benchmarks/latency/latency_histogram.py ${FIGURE_OUTPUT_DIR}/latency.pdf
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/benchmarks/latency
    DEPENDS
        ${PROJECT_SOURCE_DIR}/benchmarks/latency/1sub-noepoll-notmpfs.log
        ${PROJECT_SOURCE_DIR}/benchmarks/latency/1sub-epoll-notmpfs.log
        ${PROJECT_SOURCE_DIR}/benchmarks/latency/1sub-epoll-tmpfs.log
)

add_custom_command (
    OUTPUT ${FIGURE_OUTPUT_DIR}/subscribers.pdf
    COMMAND ${PYTHON_EXECUTABLE}
    ARGS ${PROJECT_SOURCE_DIR}/benchmarks/multi_client/read_times.py ${FIGURE_OUTPUT_DIR}/subscribers.pdf
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/benchmarks/multi_client
)

add_custom_command (
    OUTPUT ${PROJECT_BINARY_DIR}/comet.pdf
    COMMAND ${LATEXMK_EXECUTABLE}
    ARGS -pdf -pdflatex=\"pdflatex --shell-escape %O %S\" ${PROJECT_BINARY_DIR}/comet.tex
    DEPENDS
        ${FIGURE_OUTPUT_DIR}/vtp.pdf
        ${FIGURE_OUTPUT_DIR}/latency.pdf
        ${FIGURE_OUTPUT_DIR}/subscribers.pdf
        ${PROJECT_BINARY_DIR}/comet.tex
)

add_custom_target (paper ALL echo
    DEPENDS ${PROJECT_BINARY_DIR}/comet.pdf
)
