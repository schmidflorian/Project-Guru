import os
import pandas
import pyodbc
import pandas as pd
from dotenv import load_dotenv


def get_mail_contents(proj_id: int, proj_type: str) -> list[str]:
    """
    retrieves mails from ixintrexx db
    :param proj_id:
    :param proj_type:
    :return:
    """
    load_dotenv()
    server = r"erne552.ernebau.local"
    database = 'ixintrexx'
    username = os.environ.get("DB_USER_NAME")
    password = os.environ.get("DB_USER_PASSWORD")
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()

    query = """
        SELECT
            STRID AS 'ID',
            XTO AS 'TO',
            XCC AS 'CC',
            XBCC AS 'BCC',
            XFROM AS 'FROM',
            XSUBJECT AS 'SUBJECT',
            XCONTENT AS 'CONTENT'
        FROM XARCHIV_MAIL
        WHERE REF_PROJ_ID = 10325 AND REF_PROJ_TYP = 'AUF'
    """
    df = pd.read_sql(query, cnxn)

    mail_contents: list = []
    for index, row_dict in df.iterrows():
        mail_content:str = ""
        for row_key, row_element in row_dict.items():
            mail_content += f"{row_key}: {row_element}\n"
        mail_contents.append(mail_content)
    return mail_contents