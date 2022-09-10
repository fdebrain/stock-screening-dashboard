import uuid

import streamlit as st
from streamlit_elements import elements, mui, nivo

CONFIG = {
    "motionConfig": "wobbly",
    "theme": {
        "background": "#FFFFFF",
        "textColor": "#31333F",
        "legends": {"text": {"text-transform": "capitalize"}},
        "axis": {"ticks": {"text": {"text-transform": "capitalize"}}},
        "tooltip": {
            "container": {
                "background": "#FFFFFF",
                "color": "#31333F",
                "fontSize": 16,
                "text-transform": "capitalize",
            }
        },
    },
}

RADAR_CONFIG = {
    "gridShape": "linear",
    "gridLabelOffset": 20,
    "dotSize": 5,
    "dotColor": {"from": "color"},
    "borderColor": {"from": "color", "modifiers": []},
    "dotBorderWidth": 2,
}

BAR_CONFIG = {
    "valueFormat": ">-.2f",
    "padding": 0.3,
    "borderWidth": 1,
    "borderColor": {"from": "color", "modifiers": [["darker", "2"]]},
    "axisBottom": {
        "tickSize": 5,
        "tickPadding": 5,
        "tickRotation": 0,
        "legendPosition": "middle",
        "legendOffset": 32,
        "legend": "Axis X",
    },
    "axisLeft": {
        "tickSize": 5,
        "tickPadding": 5,
        "tickRotation": 0,
        "legendPosition": "middle",
        "legendOffset": -40,
        "legend": "Axis Y",
    },
    "labelSkipWidth": 12,
    "labelSkipHeight": 12,
    "legends": [
        {
            "anchor": "bottom-right",
            "direction": "column",
            "translateX": 150,
            "translateY": 0,
            "itemsSpacing": 2,
            "itemWidth": 100,
            "itemHeight": 20,
            "symbolSize": 20,
            "effects": [{"on": "hover", "style": {"itemTextColor": "#000"}}],
        }
    ],
}


PIE_CONFIG = {
    "margin": {"top": 30, "right": 30, "bottom": 30, "left": 30},
    "colors": {"scheme": "nivo"},
    "activeOuterRadiusOffset": 5,
    "innerRadius": 0.5,
    "padAngle": 0.7,
    "cornerRadius": 2,
    "borderWidth": 1,
    "borderColor": {"from": "color", "modifiers": [["darker", "2"]]},
    "arcLinkLabelsThickness": 2,
    "arcLinkLabelsColor": {"from": "color"},
    "arcLinkTextColor": {"from": "color", "modifiers": [["darker", "2"]]},
    "arcLabelsSkipAngle": 10,
    "arcLinkLabelsSkipAngle": 10,
    "arcLinkLabelsDiagonalLength": 20,
    "valueFormat": " >-2.1~f",
}


LINE_CONFIG = {
    "margin": {"top": 120, "right": 150, "bottom": 50, "left": 60},
}


def plot_pie(df, col_cat: str, col_val: str):
    with elements(str(uuid.uuid4())):
        with mui.Box(sx={"height": 400}):
            data = list(
                df[[col_cat, col_val]]
                .rename(columns={col_cat: "id", col_val: "value"})
                .to_dict(orient="index")
                .values()
            )

            nivo.Pie(
                data=data,
                **CONFIG,
                **PIE_CONFIG,
            )


def plot_line(df, col_x, col_y):
    color = st.color_picker("Pick a color", value="#3664E0", key="line_color")
    st.vega_lite_chart(
        df,
        {
            "width": 700,
            "config": {"view": {"stroke": None}},
            "mark": {"type": "line", "tooltip": True},
            "encoding": {
                "x": {"field": col_x, "type": "temporal"},
                "y": {"field": col_y, "type": "quantitative"},
                "color": {"value": color},
            },
        },
    )


def plot_bar(df, col_x, col_y):
    color = st.color_picker("Pick a color", value="#3664E0", key="bar_color")
    st.vega_lite_chart(
        df,
        {
            "width": 500,
            "config": {"view": {"stroke": None}},
            "layer": [
                {
                    "mark": {"type": "bar", "tooltip": True},
                    "encoding": {
                        "x": {"field": col_x, "type": "temporal"},
                        "y": {"field": col_y, "type": "quantitative"},
                        "color": {"value": color},
                    },
                },
                {
                    "mark": {"type": "rule", "tooltip": True},
                    "encoding": {
                        "y": {
                            "aggregate": "mean",
                            "field": col_y,
                            "type": "quantitative",
                        },
                        "color": {"value": "red"},
                        "size": {"value": 2},
                    },
                },
            ],
        },
    )


def show_dataframe(df):
    columns = [
        {
            "id": col,
            "field": col,
            "headerName": col,
            "width": 180,
        }
        for col in df.columns
    ]
    data = [{"id": id, **row} for id, row in df.to_dict(orient="index").items()]

    with mui.Box(sx={"width": 400, "height": 600}):
        mui.DataGrid(
            columns=columns,
            rows=data,
            pageSize=10,
            disableSelectionOnClick=True,
        )
