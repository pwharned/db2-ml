import nzae
from joblib import load
from io import BytesIO
import base64

class predict(nzae.Ae):
    def _setup(self):
        self.model = None

    def predict(self,data):
        model = data[0]
        if not self.model:
            self.model = load(BytesIO(base64.b64decode(model)))

        data = data[1:]
        result = self.model.predict([data])
        return float(result[0])

    def _getFunctionResult(self,row):
        price = self.predict(row)
        return price

predict.run()