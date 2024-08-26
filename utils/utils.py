import os
import pandas as pd

def root():
    starting_path = os.path.dirname(os.path.abspath(__file__))
    path_parts = starting_path.split(os.sep)
    for i in range(len(path_parts)):
        if path_parts[i] == 'DraftSculptor':
            return os.sep.join(path_parts[:i+1])
    return None

def pjoin(*x):
    return os.path.join(*x)

def check_format(df_):
    if os.path.exists(df_):
        file_name = df_
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file_name)
        elif file_name.endswith('.csv'):
            df = pd.read_csv(file_name)
        else:
            print("Unsupported file format.")
            return
    else:
        df = df_
    required_columns = {"文字", "X", "Y", "大小", "字体"}
    if not required_columns.issubset(df.columns):
        print("File does not contain the required columns.")
        return
    for i, row in df.iterrows():
        if not isinstance(row["文字"], (str, pd._libs.missing.NAType)):
            print(f"Row {i+1}: '文字' should be a string or a file path.")
            row["文字"] = str(row["文字"])
        if not isinstance(row["X"], (int, float)):
            print(f"Row {i+1}: 'X' should be a number.")
            return
        if not isinstance(row["Y"], (int, float)):
            print(f"Row {i+1}: 'Y' should be a number.")
            return
        if not isinstance(row["大小"], (int, float)):
            print(f"Row {i+1}: '大小' should be a number.")
            return
        if not isinstance(row["字体"], str):
            print(f"Row {i+1}: '字体' should be a string.")
            return
    return df
    

if __name__ == "__main__":
    draftsculptor_path = root()
    if draftsculptor_path:
        print(f"'Draftsculptor' found at: {draftsculptor_path}")
    else:
        print("'Draftsculptor' directory not found.")
    print(pjoin("a", "b"))
