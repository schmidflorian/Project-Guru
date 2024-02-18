from pathlib import Path


def get_pdf_file_paths(folder_path=r"\\ernesrv105.erne.net\Offerten Intrexx\2023_EHB_316968\01 Ausschreibung\Test Projektguru") -> list[Path]:
    """
    file crawler to extract all pdf files
    :param folder_path:
    :return:
    """
    pdf_files = []
    for file in Path(folder_path).rglob("*.pdf"):
        if file.suffix == ".pdf":
            pdf_files.append(file)
    return pdf_files
