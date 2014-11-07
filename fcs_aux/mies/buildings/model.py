from mies.celery import app


@app.task(ignore_results=True)
def create_buildings(buildings, flr):
    for bldg in buildings:
        # generate random address
        # verify (using the cache) that it's free
        pass
    # use bulk insert to write all buildings to the database
