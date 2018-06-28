
import pandas as pd

class Table:

    def __init__(self,subject_data):
        self.subject_data=subject_data
        decimals = pd.Series([4,2],index=['Values','Z-scores'])
        self.subject_data=self.subject_data.round(decimals)
    def frame_to_list(self):
        temp = [['Region', 'Value', 'Z-score']]
        for row in self.subject_data.iterrows():
            index, data = row
            temp.append([index]+data.tolist())

        return temp
