set(Namespace_SRCS
    freecad/_4d_overview_wb/init_gui.py
    freecad/_4d_overview_wb/__init__.py
    freecad/_4d_overview_wb/version.py
    freecad/_4d_overview_wb/resources/4doverview.svg
    freecad/_4d_overview_wb/resources/translations/_4d_overview_wb_es-ES.qm
    freecad/_4d_overview_wb/resources/translations/_4d_overview_wb_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(4DOVERVIEW ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(4DOVERVIEW "${CMAKE_BINARY_DIR}/Mod/4DOverview" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/4DOverview
)
