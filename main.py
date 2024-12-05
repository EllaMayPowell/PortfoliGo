from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        try:
            # Handle file upload
            file = request.files.get('file')
            if file and file.filename.endswith('.csv'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'],
                                        file.filename)
                file.save(filepath)
                return redirect(url_for('dashboard', filename=file.filename))
            else:
                # No file uploaded or invalid file type
                return redirect(url_for('dashboard', filename=None))
        except Exception as e:
            return render_template("upload.html",
                                   error=f"Error uploading file: {e}")
    return render_template("upload.html")


@app.route("/dashboard")
def dashboard():
    filename = request.args.get('filename')

    # Default example portfolio if no file is uploaded
    example_data = {
        "Asset": ["Stocks", "Bonds", "Cash"],
        "Value": [30000, 15000, 5000],
        "Allocation": [60, 30, 10]
    }
    df = pd.DataFrame(example_data)

    if filename:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            df = pd.read_csv(filepath)

            # Ensure required columns exist
            required_columns = {'Asset', 'Value', 'Allocation'}
            if not required_columns.issubset(df.columns):
                return render_template(
                    "dashboard.html",
                    error=
                    "CSV must contain 'Asset', 'Value', and 'Allocation' columns."
                )
        except Exception as e:
            return render_template("dashboard.html",
                                   error=f"Error processing the file: {e}")

    # Calculate total value and summary stats
    total_value = df['Value'].sum()
    allocations = df[['Asset', 'Allocation']].to_dict(orient='records')
    return render_template("dashboard.html",
                           total_value=total_value,
                           allocations=allocations)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
