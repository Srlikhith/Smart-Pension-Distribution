# pension_backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
# pension_backend/app.py
import csv



app = Flask(__name__)
CORS(app)
parents = []
children = {}

def load_data_from_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            parent_aadhaar = str(row['parent_aadhaar']).strip()
            child_aadhaar = str(row['child_aadhaar']).strip()

            # Add parent
            if not any(p['aadhaar'] == parent_aadhaar for p in parents):
                parents.append({
                    "aadhaar": parent_aadhaar,
                    "age": int(row['parent_age']),
                    "income": int(row['parent_income']),
                    "houseCount": int(row['parent_house_count']),
                    "ownsCar": row['parent_owns_car'].strip().lower() == 'true'
                })

            # Add child
            child = {
                "aadhaar": child_aadhaar,
                "name": row['child_name'].strip(),
                "income": int(row['child_income'])
            }

            if parent_aadhaar not in children:
                children[parent_aadhaar] = []

            if not any(c['aadhaar'] == child['aadhaar'] for c in children[parent_aadhaar]):
                children[parent_aadhaar].append(child)

load_data_from_csv("parents_children_dataset.csv")
print("Loaded parent-child data:")
for p, c_list in children.items():
    print(p, "->", [c['aadhaar'] for c in c_list])


@app.route('/api/check-eligibility', methods=['POST'])
def check_eligibility():
    data = request.json
    aadhaar = data['aadhaar']
    age = data['age']
    income = data['income']
    house_count = data['houseCount']
    owns_car = data['ownsCar']

    eligible = age >= 60 and income < 100000 and house_count <= 1 and not owns_car

    if eligible and not any(p['aadhaar'] == aadhaar for p in parents):
        parents.append({"aadhaar": aadhaar, "age": age, "income": income, "houseCount": house_count, "ownsCar": owns_car})

    return jsonify({"eligible": eligible})

@app.route('/api/add-children', methods=['POST'])
def add_children():
    data = request.json
    parent_aadhaar = data['parentAadhaar']
    children_list = data['childrenList']
    children[parent_aadhaar] = children_list
    return jsonify({"message": "Children added successfully."})

@app.route('/api/children/<aadhaar>', methods=['GET'])
def get_children(aadhaar):
    return jsonify(children.get(aadhaar, []))

@app.route('/api/check-child-contribution', methods=['POST'])
def check_child_contribution():
    data = request.json
    income = data['income']
    aadhaar = data['aadhaar']

    if income > 1500000:
        percentage = 100
    elif income > 1000000:
        percentage = 75
    elif income > 500000:
        percentage = 50
    elif income > 100000:
        percentage = 25
    else:
        percentage = 0

    contribution = (48000 * percentage) // 100
    return jsonify({"aadhaar": aadhaar, "income": income, "percentage": percentage, "contribution": contribution})

@app.route('/api/officer-dashboard', methods=['GET'])
def officer_dashboard():
    total_parents = len(parents)
    total_children = sum(len(c) for c in children.values())
    estimated_savings = total_children * 24000
    return jsonify({
        "totalParents": total_parents,
        "totalChildren": total_children,
        "estimatedGovtSavings": estimated_savings
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)