from flask import Flask, render_template

# http://localhost:5000/
# http://localhost:5000/docs

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

#region templates

@app.route("/")
def ROUTE_index():
    return render_template('index.html')

#endregion

if __name__ == "__main__":
    app.run(debug=True)