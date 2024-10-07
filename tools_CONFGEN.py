import os
import pandas as pd
import random
from datetime import datetime



example_cofig = {
    "一次性": [
        {"name": "流水号", "position": (910, 1197, 80), "字体": "宋体"},
        {"name": "车牌号", "position": (1815, 1211, 80), "字体": "宋体"},
        {"name": "日期", "position": (3121, 1206, 80), "字体": "宋体"},
        {"name": "收油人员", "position": (2664, 1206, 80), "字体": "宋体"},
    ],
    "纵向": [
        {"name": "餐厅名称", "position": (1083, 1983, 80), "间隔": 113.5, "字体": "宋体"}, 
        {"name": "桶数", "position": (2089, 1983, 80), "间隔": 113.5, "字体": "宋体"},
        {"name": "餐厅负责人", "position": (2836, 1983, 80), "间隔": 113.5, "扰动": "100 0"},
        ],
    "系统设置": {"扰动": 0, "字体": "hand"}
}

class ConfigGenerator():
    def __init__(self, file_path, conf):
        self.conf = conf
        self.check_conf_format()
        self.file_path = file_path
        self.output_path = "generated_config"
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.index_column = self.conf.get("一次性")[0]['name']
        print(f"通过 {self.index_column} 进行分隔配置文件...")
        self.dfs = self.split_df(self.index_column)
        for df in self.dfs:
            self.format_subexcel(df)
            break


    def _validate(self, obj, addkey=None):
        # Check if the object is a dictionary
        if not isinstance(obj, dict):
            return False
        # Check if 'name' is in the dictionary and if it is a string
        if 'name' not in obj or not isinstance(obj['name'], str):
            return False
        # Check if 'position' is in the dictionary, if it's a tuple, and its length is 3
        if 'position' not in obj or not isinstance(obj['position'], tuple) or len(obj['position']) != 3:
            return False
        # Check if all elements in the 'position' tuple are numeric (int or float)
        if not all(isinstance(item, (int, float)) for item in obj['position']):
            return False
        # If all checks pass, return True
        if addkey:
            if addkey not in obj:
                return False
        return True
    
    def fuzzy_search(self, tardf, key):
        def find_first_true_index(lst):
            return next((i for i, item in enumerate(lst) if item), None)
        lst = [True if key in x else False for x in tardf.columns]
        return tardf.columns[find_first_true_index(lst)]
    
    def sparse_disturb(self, x):
        if isinstance(x, int):  # "扰动": 10
            return x, x
        else:  # "扰动": 10 20
            return [int(y) for y in x.split(" ")]
            
        
    def split_df(self, key_column):
        data = pd.read_excel(self.file_path)
        key_column = self.fuzzy_search(data, key_column)
        try:
            data[key_column] = data[key_column].fillna(method='bfill')
            print(f"将 {key_column} 中的值转为整型。")
            data[key_column] = data[key_column].astype('int')
        except:
            print(f"{key_column} 无需填充。")

        # Step 2: Get unique serial numbers after filling
        unique_serial_numbers = data[key_column].unique()

        # Step 3: Split the data into separate DataFrames for each unique key_column
        df_dict = {
            serial_number: data[data[key_column] == serial_number]
            for serial_number in unique_serial_numbers if not pd.isna(serial_number)
        }
        
        dfs = []
        for serial_number, df in df_dict.items():
            dfs.append(df)
        return dfs
    
    def apply_disturbance(self, value, disturbance):
        return value + random.uniform(-disturbance, disturbance)
    
    def check_conf_format(self):
        if not "一次性" in self.conf:
            raise ValueError("至少包含一个‘一次性’键，作为统一的分隔标准，其中第一个作为分割标准。")
        else:
            for x in self.conf["一次性"]:
                flag = self._validate(x)
                if not flag:
                    print(f"{x} 不符合规定，请检查格式。")
        if "纵向" in self.conf:
            for x in self.conf["纵向"]:
                flag = self._validate(x, addkey="间隔")
                if not flag:
                    print(f"{x} 不符合规定，请检查格式。")
        if not "系统设置" in self.conf:
            print("自动分配系统设置：\"系统设置\": {\"扰动\": 20, \"字体\": \"hand\"}")
            self.conf["系统设置"] = {"扰动": 5, "字体": "hand"}
            
    
    def format_subexcel(self, df):
        tar_df_name = df[self.fuzzy_search(df, self.index_column)].iloc[0]
        print(f"正在处理 {self.index_column} 为 {tar_df_name} 的表...")
        output_data = []
        for item in self.conf["一次性"]:
            if item["name"] == '日期':
                value = str(df[self.fuzzy_search(df, item["name"])].iloc[0])
                date_obj = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                value_ = str(date_obj.strftime("%Y %m %d"))
                print(f"特殊处理日期格式，将 {value} 转换为 {value_}。")
                value = value_
            else:
                value = str(df[self.fuzzy_search(df, item["name"])].iloc[0])  # 一次性值全部取第一个
            x, y, size = item["position"]
            if "扰动" in item:
                x_dis, y_dis = self.sparse_disturb(item["扰动"])
            else:
                x_dis, y_dis = self.sparse_disturb(self.conf["系统设置"]["扰动"])
            x = self.apply_disturbance(x, x_dis)
            y = self.apply_disturbance(y, y_dis)
            font = item['字体'] if '字体' in item else self.conf["系统设置"]["字体"]
            output_data.append({"文字": value, "X": x, "Y": y, "大小": size, "字体": font})

        if "纵向" in self.conf:
            for _, conf in enumerate(self.conf["纵向"]):
                interval = conf["间隔"]
                name = self.fuzzy_search(df, conf["name"])
                x, y, size = conf["position"]
                font = item['字体'] if '字体' in conf else self.conf["系统设置"]["字体"]
                for ind, tar_name in enumerate(df[name]):
                    if "扰动" in conf:
                        x_dis, y_dis = self.sparse_disturb(conf["扰动"])
                    else:
                        x_dis, y_dis = self.sparse_disturb(self.conf["系统设置"]["扰动"])
                    disturbed_x = self.apply_disturbance(x, x_dis)
                    disturbed_y = self.apply_disturbance(y + ind * interval, y_dis)
                    output_data.append({"文字": tar_name, "X": disturbed_x, "Y": disturbed_y, "大小": size, "字体": font})

        # Create a DataFrame for the output
        output_df = pd.DataFrame(output_data)

        # Save the output to an Excel file
        output_file_path = os.path.join(self.output_path, f"{tar_df_name}.xlsx")
        output_df.to_excel(output_file_path, index=False)
        
    
    
    

if __name__ == "__main__":
    file = '7K吨餐厅表.xlsx'
    cg = ConfigGenerator(file_path=file, conf=example_cofig)
    
    