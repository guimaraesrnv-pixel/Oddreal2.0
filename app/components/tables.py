
import streamlit as st
import pandas as pd


class Tables:

    @staticmethod
    def dataframe(data):

        if not data:

            st.info("Nenhum dado disponível.")

            return

        st.dataframe(pd.DataFrame(data))
