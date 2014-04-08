project (comet-paper)
cmake_minimum_required (VERSION 2.8)

set (CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set (FIGURE_OUTPUT_DIR ${PROJECT_BINARY_DIR}/figures)

find_package (LATEX REQUIRED)
find_package (LATEXMK REQUIRED)
find_package (PYTHONINTERP REQUIRED)

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
    ${PROJECT_SOURCE_DIR}/figures/vtp.pdf
    ${FIGURE_OUTPUT_DIR}/vtp.pdf
    COPYONLY
)

configure_file (
    ${PROJECT_SOURCE_DIR}/figures/tcp.pdf
    ${FIGURE_OUTPUT_DIR}/tcp.pdf
    COPYONLY
)

if (IS_DIRECTORY ${COMET_BENCHMARK_DATA})
    message (STATUS "Got raw benchmark measurements")
    add_custom_command (
        OUTPUT ${FIGURE_OUTPUT_DIR}/latency.json
        COMMAND ${PYTHON_EXECUTABLE}
        ARGS ${PROJECT_SOURCE_DIR}/figures/latency.py aggregate
             ${COMET_BENCHMARK_DATA}/latency/1sub-noepoll-notmpfs.log
             ${COMET_BENCHMARK_DATA}/latency/1sub-epoll-notmpfs.log
             ${COMET_BENCHMARK_DATA}/latency/1sub-epoll-tmpfs.log
             ${FIGURE_OUTPUT_DIR}/latency.json
        DEPENDS
             ${COMET_BENCHMARK_DATA}/latency/1sub-noepoll-notmpfs.log
             ${COMET_BENCHMARK_DATA}/latency/1sub-epoll-notmpfs.log
             ${COMET_BENCHMARK_DATA}/latency/1sub-epoll-tmpfs.log
    )
    add_custom_command (
        OUTPUT ${FIGURE_OUTPUT_DIR}/multisubscriber.json
        COMMAND ${PYTHON_EXECUTABLE}
        ARGS ${PROJECT_SOURCE_DIR}/figures/multisubscriber.py aggregate
             ${COMET_BENCHMARK_DATA}/multisubscriber
             ${FIGURE_OUTPUT_DIR}/multisubscriber.json
        DEPENDS
             ${COMET_BENCHMARK_DATA}/multisubscriber
    )
    add_custom_command (
        OUTPUT ${FIGURE_OUTPUT_DIR}/throughput.json
        COMMAND ${PYTHON_EXECUTABLE}
        ARGS ${PROJECT_SOURCE_DIR}/figures/throughput.py aggregate
             ${COMET_BENCHMARK_DATA}/throughput
             ${FIGURE_OUTPUT_DIR}/throughput.json
        DEPENDS
             ${COMET_BENCHMARK_DATA}/throughput
    )
else (IS_DIRECTORY ${COMET_BENCHMARK_DATA})
    message (STATUS "Raw Benchmark data not available; using defaults")
    configure_file (
        ${PROJECT_SOURCE_DIR}/figures/latency.json
        ${FIGURE_OUTPUT_DIR}/latency.json
        COPYONLY
    )
    configure_file (
        ${PROJECT_SOURCE_DIR}/figures/multisubscriber.json
        ${FIGURE_OUTPUT_DIR}/multisubscriber.json
        COPYONLY
    )
    configure_file (
        ${PROJECT_SOURCE_DIR}/figures/throughput.json
        ${FIGURE_OUTPUT_DIR}/throughput.json
        COPYONLY
    )
endif (IS_DIRECTORY ${COMET_BENCHMARK_DATA})

add_custom_command (
    OUTPUT ${FIGURE_OUTPUT_DIR}/latency.pdf
    COMMAND ${PYTHON_EXECUTABLE}
    ARGS ${PROJECT_SOURCE_DIR}/figures/latency.py plot
         ${FIGURE_OUTPUT_DIR}/latency.json
         ${FIGURE_OUTPUT_DIR}/latency.pdf
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/figures
    DEPENDS ${FIGURE_OUTPUT_DIR}/latency.json
)

add_custom_command (
    OUTPUT ${FIGURE_OUTPUT_DIR}/subscribers.pdf
    COMMAND ${PYTHON_EXECUTABLE}
    ARGS ${PROJECT_SOURCE_DIR}/figures/multisubscriber.py plot
         ${FIGURE_OUTPUT_DIR}/multisubscriber.json
         ${FIGURE_OUTPUT_DIR}/subscribers.pdf
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/figures
    DEPENDS ${FIGURE_OUTPUT_DIR}/multisubscriber.json
)

add_custom_command (
    OUTPUT ${FIGURE_OUTPUT_DIR}/throughput.pdf
    COMMAND ${PYTHON_EXECUTABLE}
    ARGS ${PROJECT_SOURCE_DIR}/figures/throughput.py plot_tp
         ${FIGURE_OUTPUT_DIR}/throughput.json
         ${FIGURE_OUTPUT_DIR}/throughput.pdf
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/figures
    DEPENDS ${FIGURE_OUTPUT_DIR}/throughput.json
)

add_custom_command (
    OUTPUT ${FIGURE_OUTPUT_DIR}/rtt.pdf
    COMMAND ${PYTHON_EXECUTABLE}
    ARGS ${PROJECT_SOURCE_DIR}/figures/throughput.py plot_rtt
         ${FIGURE_OUTPUT_DIR}/throughput.json
         ${FIGURE_OUTPUT_DIR}/rtt.pdf
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/figures
    DEPENDS ${FIGURE_OUTPUT_DIR}/throughput.json
)

add_custom_command (
    OUTPUT ${PROJECT_BINARY_DIR}/comet.pdf
    COMMAND ${LATEXMK_EXECUTABLE}
    ARGS -pdf -pdflatex=\"pdflatex --shell-escape %O %S\" ${PROJECT_BINARY_DIR}/comet.tex
    DEPENDS
        ${FIGURE_OUTPUT_DIR}/vtp.pdf
        ${FIGURE_OUTPUT_DIR}/tcp.pdf
        ${FIGURE_OUTPUT_DIR}/latency.pdf
        ${FIGURE_OUTPUT_DIR}/subscribers.pdf
        ${FIGURE_OUTPUT_DIR}/throughput.pdf
        ${FIGURE_OUTPUT_DIR}/rtt.pdf
        ${PROJECT_BINARY_DIR}/comet.tex
)

add_custom_target (paper ALL echo
    DEPENDS ${PROJECT_BINARY_DIR}/comet.pdf
)
