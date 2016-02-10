from flask import Flask, json
import pymysql


app = Flask(__name__)


def vehicle(vin=None, make=None, model=None, year=None):
    ret_veh = {"vin": vin, "make": make, "model": model, "year": year}
    return ret_veh


@app.route('/vin_service/v1/<make>/<year>')
@app.route('/vin_service/v1/<string:make>')
@app.route('/vin_service/v1/<int:year>')
def vin_service(make=None, year=None):
    no_make = 'SELECT VIN, vehicle_make, vehicle_model, vehicle_Year FROM vins WHERE vehicle_Year = %s limit 1'
    no_year = 'SELECT VIN, vehicle_make, vehicle_model, vehicle_Year FROM vins WHERE vehicle_make = %s limit 1'
    make_year = 'SELECT VIN, vehicle_make, vehicle_model, vehicle_Year FROM vins WHERE vehicle_Make = %s AND ' \
                'vehicle_Year = %s limit 1'

    # Connect to database
    config = {'user': 'dtqa', 'password': '7roppu$', 'host': 'dmssjosln01.dt.inc',
              'port': 3306, 'database': 'dtautomation'}
    conn = pymysql.connect(**config)
    connect = conn.cursor()
    # Query the database
    # Get a VIN from the VINS database
    if make is None:
        connect.execute(no_make, (year, ))
    elif year is None:
        connect.execute(no_year, (make,))
    else:
        connect.execute(make_year, (make, year))

    used_vin = connect.fetchall()
    # Delete the used vin from database so it cannot be used again
    connect.execute('DELETE FROM vins WHERE VIN = %s', (used_vin[0][0],))
    conn.commit()
    return str(json.dumps(vehicle(*(used_vin[0]))))


@app.errorhandler(500)
def internal_server_error():
    return str(json.dumps({"message": "There was a problem with the parameters provided"})), 500


@app.errorhandler(404)
def page_not_found():
    return str(json.dumps({"message": "There is a problem with the URL you typed in"})), 404

if __name__ == '__main__':
    app.run(debug=False)
