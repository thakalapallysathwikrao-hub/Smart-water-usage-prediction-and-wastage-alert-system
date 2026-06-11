from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)
DATA_FILE = 'water_usage.csv'

@app.route("/", methods=["GET", "POST"])
def index():
    if not os.path.exists(DATA_FILE):
        return "Error: water_usage.csv file not found!"

    # Load dataset for benchmark
    df = pd.read_csv(DATA_FILE)
    df.columns = df.columns.str.strip()
    avg_dataset = round(df['water_usage'].mean())

    if request.method == "POST":
        # Capture Inputs
        people = int(request.form.get("people", 0))
        temp = int(request.form.get("temperature", 0))
        day_type = request.form.get("day_type")
        
        # Weighted Logical Model
        base_demand = people * 135
        heat_penalty = (temp - 25) * 10 if temp > 25 else 0
        day_surge = 1.2 if day_type == 'weekend' else 1.0
        
        prediction = round((base_demand + heat_penalty) * day_surge)
        per_person = round(prediction / people) if people > 0 else 0
        
        # Status Categorization
        if per_person > 180:
            status, status_color = "Critical: Heavy Usage", "#ef4444"
        elif per_person > 140:
            status, status_color = "Warning: Moderate Usage", "#f59e0b"
        else:
            status, status_color = "Success: Efficient Usage", "#22c55e"
            
        return render_template("index.html", 
                               show_report=True,
                               prediction=prediction,
                               avg_dataset=avg_dataset,
                               per_person=per_person,
                               people_impact=base_demand,
                               heat_impact=round(heat_penalty * day_surge),
                               day_impact=round((base_demand + heat_penalty) * (day_surge - 1)),
                               status=status,
                               status_color=status_color,
                               day=day_type.capitalize())
                               
    return render_template("index.html", show_report=False)

if __name__ == "__main__":
    app.run(debug=True)