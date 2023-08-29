from . import connector
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect  
from django.template import loader
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
import os.path as path
import os
matplotlib.use('agg')
# Create your views here.

connector.cur.execute("""CREATE TABLE IF NOT EXISTS Users(
                      id SERIAL PRIMARY KEY NOT NULL,
                      Username VARCHAR(1000),
                      Email VARCHAR(1000),
                      Password VARCHAR(1000));"""
)

# CSV file which stores all of the categoryname, cataegorycolour, categoryvalue

def SignUp(response):
    if response.method == "POST":
        Username = response.POST["Username"]
        global Email
        Email = response.POST["Email"]
        Password = response.POST["Password"]

        connector.cur.execute("""SELECT id FROM Users WHERE Email = %s;""", [Email])

        try:
            id = ((connector.cur.fetchall()[0])[0])
            return render(response, "main/SignUpPage.html", {"ErrorMessage":"Email is already being used."})
        
        except:
            connector.cur.execute("""INSERT INTO Users (Username, Email, Password) VALUES
                                  (%s, %s, %s);""", [Username, Email, Password])
            connector.conn.commit()

            TotalIncome = {
                "IncomeCategoryName": [],
                "IncomeCategoryValue": [],
                "TotalIncome": []
            }

            TotalOutcome = {
                "OutcomeCategoryName": [],
                "OutcomeCategoryValue": [],
                "TotalOutcome": []
            }

            TotalIncomeDF = pd.DataFrame(TotalIncome)
            TotalOutcomeDF = pd.DataFrame(TotalOutcome)

            connector.cur.execute("""SELECT id FROM Users WHERE Email = %s;""", [Email])
            id = ((connector.cur.fetchall()[0])[0])

            TotalIncomeCSVName = "main/TotalIncome" + str(id) + ".csv"
            TotalOutcomeCSVName = "main/TotalOutcome" + str(id) + ".csv"

            TotalIncomePath = path.abspath(path.join(TotalIncomeCSVName))
            TotalOutcomePath = path.abspath(path.join(TotalOutcomeCSVName))

            TotalIncomeDF.to_csv(TotalIncomePath, index=False)
            TotalOutcomeDF.to_csv(TotalOutcomePath, index=False)

            return redirect("/Home")
            
    else:
        return render(response, "main/SignUpPage.html", {})
    
def Login(response):
    if response.method == "POST":
        Username = response.POST["Username"]
        Password = response.POST["Password"]

        connector.cur.execute("""SELECT id FROM Users WHERE Username = %s AND Password = %s;""", [Username, Password])

        try:
            id = ((connector.cur.fetchall()[0])[0])
            connector.cur.execute("""SELECT Email FROM Users WHERE Username = %s AND Password = %s;""", [Username, Password])
            global Email
            Email = ((connector.cur.fetchall()[0])[0])

            return redirect("/Home")
        
        except:
            
            return render(response, "main/LoginPage.html", {"ErrorMessage":"Login details doesn't match."})

    else:
        return render(response, "main/LoginPage.html", {})
    
def Home(response):
    connector.cur.execute("""SELECT id FROM Users WHERE Email = %s;""", [Email])
    id = ((connector.cur.fetchall()[0])[0])

    if response.method == "POST":
        try:
            # adding data from income cat name and colour
            AddingIncomeCategory = str(response.POST["AddingIncomeCategory"])
            AddingIncomeCategoryColour = str(response.POST["AddingIncomeCategoryColour"])

            TotalIncomeDF = pd.read_csv("main/TotalIncome" + str(id) + ".csv")

            if AddingIncomeCategory in (TotalIncomeDF["IncomeCategoryName"].values.tolist()):
                return render(response, "main/HomePage.html", {"ErrorMessage":"Column already exists."})

            else:
                NewIncomeCategory = {
                    "IncomeCategoryName": [AddingIncomeCategory],
                    "IncomeCategoryValue": [AddingIncomeCategoryColour],
                    "TotalIncome": [0]
                }

                NewIncomeCategoryDF = pd.DataFrame(NewIncomeCategory)
                CSVName = "main/TotalIncome" + str(id) + ".csv"
                NewIncomeCategoryDF.to_csv(CSVName, mode="a", index=False, header=False)

                return HttpResponseRedirect(response.path_info)

        except:

            try:
                # adding data from outcome cat name and col
                AddingOutcomeCategory = str(response.POST["AddingOutcomeCategory"])
                AddingOutcomeCategoryColour = str(response.POST["AddingOutcomeCategoryColour"])

                TotalOutcomeDF = pd.read_csv("main/TotalOutcome" + str(id) + ".csv")

                if AddingOutcomeCategory in (TotalOutcomeDF["OutcomeCategoryName"].values.tolist()):
                    return render(response, "main/HomePage.html", {"ErrorMessage":"Column already exists."})
                
                else:
                    NewOutcomeCategory = {
                        "OutcomeCategoryName": [AddingOutcomeCategory],
                        "OutcomeCategoryValue": [AddingOutcomeCategoryColour],
                        "TotalOutcome": [0]
                    }

                    NewOutcomeCategoryDF = pd.DataFrame(NewOutcomeCategory)
                    CSVName = "main/TotalOutcome" + str(id) + ".csv"
                    NewOutcomeCategoryDF.to_csv(CSVName, mode="a", index=False, header=False)
                    return HttpResponseRedirect(response.path_info)

            except:
                
                try:
                    # update value for total income dependent on category name
                    IncomeCategoryName = str(response.POST["IncomeCategoryName"])
                    AddingValue = int(response.POST["InputCategoryIncome"])
                    CSVName = "main/TotalIncome" + str(id) + ".csv"
                    TotalIncomeDF = pd.read_csv(CSVName)

                    if IncomeCategoryName in (TotalIncomeDF["IncomeCategoryName"].values.tolist()):
                        IncomeData = int((TotalIncomeDF.loc[TotalIncomeDF["IncomeCategoryName"] == IncomeCategoryName]["TotalIncome"]).to_string(index=False)) + AddingValue        

                        TotalIncomeDF.loc[TotalIncomeDF["IncomeCategoryName"] == IncomeCategoryName, ["TotalIncome"]] = [IncomeData]
                        TotalIncomePath = path.abspath(path.join(CSVName))
                        TotalIncomeDF.to_csv(TotalIncomePath, index=False)

                        return HttpResponseRedirect(response.path_info)
                    
                    else:
                        return render(response, "main/HomePage.html", {"ErrorMessage":"Column doesn't exist."})
                
                except:

                    try:
                        # update value for total outcome depednent on category name
                        OutcomeCategoryName = str(response.POST["OutcomeCategoryName"])
                        AddingValue = int(response.POST["InputCategoryOutcome"])
                        CSVName = "main/TotalOutcome" + str(id) + ".csv"
                        TotalOutcomeDF = pd.read_csv(CSVName)

                        if OutcomeCategoryName in (TotalOutcomeDF["OutcomeCategoryName"].values.tolist()):
                            OutcomeData = int((TotalOutcomeDF.loc[TotalOutcomeDF["OutcomeCategoryName"] == OutcomeCategoryName]["TotalOutcome"]).to_string(index=False)) + AddingValue

                            TotalOutcomeDF.loc[TotalOutcomeDF["OutcomeCategoryName"] == OutcomeCategoryName, ["TotalOutcome"]] = [OutcomeData]
                            TotalOutcomePath = path.abspath(path.join(CSVName))
                            TotalOutcomeDF.to_csv(TotalOutcomePath, index=False)

                            return HttpResponseRedirect(response.path_info)
                        
                        else:
                            return render(response, "main/HomePage.html", {"ErrorMessage":"Column doesn't exist."})

                    except:
                        return render(response, "main/HomePage.html", {"ErrorMessage":"You haven't filled out enough information."})

                    

    else:

        TotalIncomeDF = pd.read_csv("main/TotalIncome" + str(id) + ".csv")
        TotalIncomeLabels = TotalIncomeDF["IncomeCategoryName"].values.tolist()
        TotalIncomeColours = TotalIncomeDF["IncomeCategoryValue"].values.tolist()
        TotalIncomeValues = TotalIncomeDF["TotalIncome"].values.tolist()   

        plt.pie(TotalIncomeValues, labels=TotalIncomeLabels, colors=TotalIncomeColours, autopct="%.2f %%")
        plt.title("Distribution of income")
        plt.savefig("main/static/main/media/TotalIncomeChart.png")
        plt.close()

        TotalOutcomeDF = pd.read_csv("main/TotalOutcome" + str(id) + ".csv")
        TotalOutcomeLabels = TotalOutcomeDF["OutcomeCategoryName"].values.tolist()
        TotalOutcomeColours = TotalOutcomeDF["OutcomeCategoryValue"].values.tolist()
        TotalOutcomeValues = TotalOutcomeDF["TotalOutcome"].values.tolist()

        plt.pie(TotalOutcomeValues, labels=TotalOutcomeLabels, colors=TotalOutcomeColours, autopct="%.2f %%")
        plt.title("Distribution of outcome")
        plt.savefig("main/static/main/media/TotalOutcomeChart.png")
        plt.close()
        #plt.text(i, TotalOutcomeValues[i], TotalOutcomeValues[i], ha = "center")
    

        template = loader.get_template("main/HomePage.html")
        context = {}
        return HttpResponse(template.render(context, response))
        #return render(response, "main/HomePage.html", {})


def Comparison(response):
    connector.cur.execute("""SELECT id FROM Users WHERE Email = %s;""", [Email])
    id = ((connector.cur.fetchall()[0])[0])

    TotalIncomeDF = (pd.read_csv("main/TotalIncome" + str(id) + ".csv")).sort_values(["TotalIncome"], ascending=False)
    OverallIncome = sum(TotalIncomeDF["TotalIncome"].values.tolist())
    TotalIncomeLabels = TotalIncomeDF["IncomeCategoryName"].values.tolist()
    TotalIncomeColours = TotalIncomeDF["IncomeCategoryValue"].values.tolist()
    TotalIncomeValues = TotalIncomeDF["TotalIncome"].values.tolist()  

    TotalOutcomeDF = (pd.read_csv("main/TotalOutcome" + str(id) + ".csv")).sort_values(["TotalOutcome"], ascending=False)
    OverallOutcome = sum(TotalOutcomeDF["TotalOutcome"].values.tolist())
    TotalOutcomeLabels = TotalOutcomeDF["OutcomeCategoryName"].values.tolist()
    TotalOutcomeColours = TotalOutcomeDF["OutcomeCategoryValue"].values.tolist()
    TotalOutcomeValues = TotalOutcomeDF["TotalOutcome"].values.tolist() 

    plt.bar(TotalIncomeLabels, TotalIncomeValues, color=TotalIncomeColours)
    plt.title("Income comparison")
    plt.xlabel("Different incomes")
    plt.ylabel("Amount of income")
    for i in range(len(TotalIncomeLabels)):
        plt.text(i, TotalIncomeValues[i], TotalIncomeValues[i], ha = "center")
    plt.savefig("main/static/main/media/CompareIncome.png")
    plt.close()

    plt.bar(TotalOutcomeLabels, TotalOutcomeValues, color=TotalOutcomeColours)
    plt.title("Outcome comparison")
    plt.xlabel("Different outcomes")
    plt.ylabel("Amount of outcome")
    for i in range(len(TotalOutcomeLabels)):
        plt.text(i, TotalOutcomeValues[i], TotalOutcomeValues[i], ha = "center")
    plt.savefig("main/static/main/media/CompareOutcome.png")
    plt.close()

    plt.bar(["Income", "Outcome"], [OverallIncome, OverallOutcome], color=["Green", "Red"])
    plt.title("Income and outcome")
    plt.xlabel("Money in and out")
    plt.ylabel("Amount of money")
    plt.text(0, OverallIncome, OverallIncome, ha = "center")
    plt.text(1, OverallOutcome, OverallOutcome, ha = "center")
    plt.savefig("main/static/main/media/CompareBoth.png")
    plt.close()
    template = loader.get_template("main/Comparison.html")
    context = {}
    MoneyRemain = OverallIncome - OverallOutcome

    if MoneyRemain < 0:
        return HttpResponse(template.render({"OverBudget": "You're £" + str(MoneyRemain * -1) + " outside of your budget."}, response))

    elif MoneyRemain > 0:
        return HttpResponse(template.render({"InBudget": "You're £" + str(MoneyRemain) + " within your budget."}, response))

    elif MoneyRemain == 0:
        return HttpResponse(template.render({"MetBudget": "You've met your budget."}, response))
