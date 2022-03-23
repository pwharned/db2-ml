from sklearn.linear_model import LinearRegression
from sklearn import datasets
import joblib
import base64
train = datasets.load_iris().get("data")
target = datasets.load_iris().get("target")
lr = LinearRegression()
lr = lr.fit(train, target)

print(lr.predict(train))

joblib.dump(lr, "linear.joblib")

with open("linear.joblib", "rb") as file:
    file =  file.read()
    b64model = base64.b64encode(file)
    print(b64model)

with open("linearmodel.b64", "wb") as file:
    file.write(b64model)
