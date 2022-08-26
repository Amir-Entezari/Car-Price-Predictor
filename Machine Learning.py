
import mysql.connector
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

#Define Model class
class Model:
    def __init__(self, database) -> None:
        self.database = database
    #PREPROCESSING THE DATA
    def preProcess(self): 
        #firsst convert data from array to dataframe
        df = pd.DataFrame()
        df['brand'] = [i[1] for i in self.database]
        df['carModel'] = [i[2] for i in self.database]
        df['yearUsed'] = [i[3] for i in self.database]
        df['milesAge'] = [round(i[4]/100)*100 for i in self.database]
        df['price'] = [round(i[5]/1000)*1000 for i in self.database]

        print(df)
        #Because we have some categorical feature, we have to use get_dummies()
        X = pd.get_dummies(df[['brand','carModel','yearUsed','milesAge']],drop_first=True)
        y = df['price']
        #At the end, we split the data to train and test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

        return X_train, X_test, y_train, y_test
    #BUILDING THE MODEL
    def build_Model(self,X_train, X_test, y_train):
        classifier = DecisionTreeClassifier()
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)
        return y_pred
    #CALCULATING THE ACCURACY
    def calcAccuracy(self,y_test,y_pred):#In this function we compare original price with predicted price and calculate the accuracy
        accuracy=[]
        for i in range(len(list(y_pred))):
            if abs(list(y_pred)[i]-list(y_test)[i])<5000:
                accuracy.append(1)
            else:
                accuracy.append(0)

        print("The accuracy of model is: ",accuracy.count(1)/len(accuracy),"with Error calculation ±2500$")



if __name__ == "__main__":
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='learn')
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM truecar')
    db =  cursor.fetchall()

    myModel = Model(db)
    X_train, X_test, y_train, y_test = myModel.preProcess()

    y_pred=myModel.build_Model(X_train, X_test, y_train)

    myModel.calcAccuracy(y_test,y_pred)
