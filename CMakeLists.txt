set(Namespace_SRCS
        freecad/_4d_overview_wb/init_gui.py
        freecad/_4d_overview_wb/__init__.py
        freecad/_4d_overview_wb/my_numpy_function.py
        freecad/_4d_overview_wb/version.py
        freecad/_4d_overview_wb/resources/cool.svg
        freecad/_4d_overview_wb/resources/translations/_4d_overview_wb_es-ES.qm
        freecad/_4d_overview_wb/resources/translations/_4d_overview_wb_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/4DOverviewWB" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
