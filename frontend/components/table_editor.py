import streamlit as st

def render_table(df):
    st.caption(f"Showing {len(df)} rows")
    df["delete"] = False

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "delete": st.column_config.CheckboxColumn("Delete?")
        },
        key="editor"
    )
    return edited_df
