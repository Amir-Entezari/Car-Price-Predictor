
from multiprocessing.reduction import duplicate
import mysql.connector
import time
import requests
from bs4 import BeautifulSoup



def carDetail(carname):
    carname= carname.replace(u'\xa0', u' ')
    j=5
    while carname[j]!=' ':
        j+=1
    caryear = carname[0:4]
    carbrand = carname[5:j]
    carmodel = carname[j+1::]
    return caryear,carbrand[0].lower()+carbrand[1::],carmodel

def intPrice(price):
    ans = ""
    for i in price:
        if ord(i)<=57 and ord(i)>=48:
            ans+=i
    return int(ans)



#DEFINE DATABASE CLASS
class Database:
    def __init__(self) :
        print("Connecting to mySQL...")
        self.cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='learn')
        self.cursor = self.cnx.cursor()
        print("Connected to mySQL")

    def createDB(self):
        self.cursor.execute('CREATE TABLE truecar(id INT, brand varchar(20), carModel varchar(20), yearUsed INT , milesAge INT, price INT)')
        print("Table truecar Created")

    def selectDB(self):
        self.cursor.execute('SELECT * FROM truecar')
        db =  self.cursor.fetchall()
        return db

    def deleteDB(self):
        self.cursor.execute('DELETE FROM truecar')
        self.cnx.commit()
        print("Table truecar Deleted")

    def getCNX(self):
        return self.cnx

    def getCursor(self):
        return self.cursor



#DEFINE WEBSCRAPPER CLASS for Truecar.com
class WebScrapping:
    def __init__(self, database):
        self.database= database
    
    #In this function we get info of all specefic brand's cars in a page
    def getPageCars(self,car,i):
        r = requests.get("https://www.truecar.com/used-cars-for-sale/listings/%s/location-santa-monica-ca/?page=%s"%(car,str(i)))
        soup = BeautifulSoup(r.text, 'html.parser')
        allCars= soup.find_all('a', attrs={'data-test':'vehicleCardLink'},href=True)
        #print(allCars)

        self.database.getCursor().execute('SELECT id FROM truecar WHERE brand = \'%s\' ORDER BY id DESC LIMIT 1;'%(car))
        lstIndex= self.database.getCursor().fetchall()
        #print(len(allCars))
        return allCars, lstIndex

    #In this function we insert all cars (that we get in above function) to our Database
    def insertPageCars(self,allCars,lst):
        if len(lst)==0:
            lst.append(0)
            lst=lst[0]
        else:
            lst=lst[0][0]+1
        for res in allCars:
            if(lst<=50):
                car = requests.get("https://www.truecar.com"+res['href'])
                carSoup = BeautifulSoup(car.text, 'html.parser')
                carName=carSoup.find('div',attrs={'class':'heading-2 margin-bottom-2', 'data-qa':"Heading"}) #Examples: 2018 Tesla Model X
                
                yearUsed, carBrand, carModel=carDetail(carName.text)
                carMileage=carSoup.find('p',attrs={'class':'margin-top-1'})
                carPrice=carSoup.find('div',attrs={'class':'heading-2 margin-top-1','data-test':'vdpPreProspectPrice','data-qa':'Heading'})

                print(lst ,carBrand , carModel, 2022-int(yearUsed),intPrice(carMileage.text),intPrice(carPrice.text))
                if (len(carModel)<=20):
                    self.database.getCursor().execute('INSERT INTO truecar VALUES (%i,\'%s\',\'%s\',%i,%i,%i)'%(lst ,carBrand , carModel, 2022-int(yearUsed),intPrice(carMileage.text),intPrice(carPrice.text)))
                    self.database.getCNX().commit()
                    lst+=1

                time.sleep(1)

    #In this function we loop over the brands and call 2 above functions
    def loopAllCars(self):
        carModels = [  'volvo'] 
        for car in carModels:
            for i in (2,3):
                allCars,lst = self.getPageCars(car,i)
                self.insertPageCars(allCars,lst)


if __name__ == "__main__":
    myDB = Database()
    myDB.createDB()
    print(myDB.selectDB())
    truecar = WebScrapping(myDB)
    truecar.loopAllCars()
