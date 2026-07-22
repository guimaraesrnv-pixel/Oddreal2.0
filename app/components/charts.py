
import streamlit as st
import pandas as pd


class Charts:

    @staticmethod
    def bar_chart(data):

        if not data:

            return

        df = pd.DataFrame(data)

        st.bar_chart(df)
