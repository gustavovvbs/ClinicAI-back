import pandas as pd 
from io import StringIO 
from io import BytesIO
from http.client import HTTPException


class ExcelService:
    def __init__(self):
        self.BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def get_excel(self, 
        data: list[dict]
    ):
        try:
            df = pd.json_normalize(data)
            with BytesIO() as excel_buffer:
                df = df.to_excel(excel_buffer, index=False, sheet_name="Estudos Clínicos")
                excel_buffer.seek(0)
                return excel_buffer.getvalue()
        except Exception as e:
            raise HTTPException(f"Error generating excel: {e}")

    # def _hardcoded_column_filter(self,
    #     df: pd.DataFrame)
    # -> pd.DataFrame:

    #     columns = [

    #     ]        



