import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

#cargar los datos
data = pd.read_csv("housing.csv")

#separar variables independientes (x) y dependiente (y)
x = data[['median_income', 'total_rooms', 'housing_median_age']]
y = data ['median_house_value']

#dividir los datos de entenamiento y prueba
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

#crear y entrenar modelo
modelo = LinearRegression()
modelo.fit(x_train, y_train)

#realizar predicciones
y_pred = modelo.predict(x_test)

#evaluar modelo
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print('Error cuadrático medio: ', mse)
print('Coeficiente de determinación: ', r2)
print('Coeficientes: ', modelo.coef_)
print('Intercepto: ', modelo.intercept_)