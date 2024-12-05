import pandas as pd
from io import BytesIO


class ExcelService:
    def get_excel(self, data: dict) -> bytes:
        try:
            # Normaliza os dados em um DataFrame
            df = pd.json_normalize(data.get("studies", []), max_level=1)

            # Gera o Excel em um buffer
            with BytesIO() as excel_buffer:
                df.to_excel(excel_buffer, index=False, sheet_name="Estudos Clínicos")
                excel_buffer.seek(0)
                return excel_buffer.getvalue()
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar o Excel: {e}")
