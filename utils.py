import streamlit as st
import altair as alt

# Create Altair bar chart
def create_bar_chart(data, x_axis, y_axis, title, x_title, y_title, color):
    chart = alt.Chart(data).mark_bar(color=f"{color}").encode(
        y=alt.Y(f"{y_axis}", sort="-x", title=f"{y_title}"),        # Y-axis title
        x=alt.X(f"{x_axis}", title=f"{x_title}"),    # X-axis title
    ).properties(
        title=f"{title}",
        width=600,
        height=400,
    )

    st.altair_chart(chart, use_container_width=True)