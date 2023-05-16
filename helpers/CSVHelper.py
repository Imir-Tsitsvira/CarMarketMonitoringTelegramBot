from pathlib import Path
import pandas as pd


class CSVHelper:
    def write(self, path, data, headers):
        df = pd.DataFrame(data, columns=headers)
        if Path.is_file(path):
            df.to_csv(path, mode='a', index=False, header=False)
        else:
            df.to_csv(path, mode='w', index=False)

    def read(self, path):
        df = pd.read_csv(path, header=None)
        return df