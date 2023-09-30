import pandas as pd
import numpy as np
from fastparquet import write

df = pd.DataFrame({'rand': np.random.random(100)})
write('sample.parquet', df, append=True)
print(pd.read_parquet('sample.parquet'))
