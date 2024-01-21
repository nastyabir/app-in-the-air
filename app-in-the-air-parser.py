import pandas as pd

class TripDataParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.trip_data = None
        self.parse_trips_data()

    def parse_trips_data(self):
        with open(self.file_path, 'r') as file:
            content = file.read()
        trip_records = content.split('trips:\n')[1].split('\n\n\n')
        data = [self.extract_flight_data(record) for record in trip_records if record.strip()]
        flattened_data = [item for sublist in data for item in sublist]
        self.trip_data = pd.DataFrame(flattened_data)
        self.process_data()

    def extract_flight_data(self, record):
        parts = record.split('\n')
        ownership_data = parts[0]
        flights = self.get_flights(parts)
        return [{'Ownership': ownership_data, 'Flight': flight} for flight in flights]

    def get_flights(self, parts):
        capture = False
        flights = []
        for part in parts:
            if part.startswith('flights:'):
                capture = True
                continue
            if any(part.startswith(x) for x in ['hotels:', 'rental cars:', 'expenses:']):
                capture = False
                continue
            if capture and part.strip():
                flights.append(part.strip())
        return flights

    def process_data(self):
        self.trip_data['Ownership'] = self.trip_data['Ownership'].apply(self.parse_ownership)
        self.trip_data = self.trip_data[self.trip_data['Ownership'] == 'mine']
        self.extract_flight_details()

    @staticmethod
    def parse_ownership(row):
        ownership_type = row.split(';')[0]
        return 'unsorted' if ownership_type == 'Ownership.UNKNOWN' else 'mine'

    def extract_flight_details(self):
        flight_details = ['airline_code', 'flight_number', 'aircraft', 'origin', 'destination', 'flight_date']
        self.trip_data[flight_details] = self.trip_data['Flight'].apply(
            lambda x: pd.Series(self.parse_flight_info(x)))
        self.trip_data['flight_date'] = pd.to_datetime(self.trip_data['flight_date'])
        self.trip_data.drop(['Ownership', 'Flight'], axis=1, inplace=True)

    @staticmethod
    def parse_flight_info(flight_info):
        parts = flight_info.split(';')
        return parts[7], parts[8], parts[9], parts[10], parts[11], parts[12]


file_path = 'data.txt'
parser = TripDataParser(file_path)
dataframe = parser.trip_data