import requests, zipfile, io
from django.core.management import BaseCommand
import pandas as pd
from django.db import transaction

from main.models import MRTLineStation, MRTLine, Station

STATIONS_URL = "https://datamall.lta.gov.sg/content/dam/datamall/datasets/PublicTransportRelated/Train%20Station%20Codes%20and%20Chinese%20Names.zip"
DEFAULT_LINE_NAMES = {
    'North-South Line': 'NSL',
    'East-West Line': 'EWL',
    'Changi Airport Branch Line': 'CGL',
    'North East Line': 'NEL',
    'Circle Line': 'CCL',
    'Circle Line Extension': 'CEL',
    'Downtown Line': 'DTL',
    'Bukit Panjang LRT': 'BPL',
    'Sengkang LRT': 'SLRT',
    'Punggol LRT': 'PLRT',
    'Thomson-East Coast Line': 'TEL'
} # used for tests


class Command(BaseCommand):
    help = "Uploads train stations from LTA DataMall, but only those which are missing from database currently."

    def add_arguments(self, parser):
        parser.add_argument(
            "--use_defaults",
            action="store_true",
            help="Uses the default MRT line codes",
        )
        pass

    def handle(self, *args, **options):
        data = requests.get(STATIONS_URL)
        z = zipfile.ZipFile(io.BytesIO(data.content))
        df = pd.read_excel(z.open("Train Station Codes and Chinese Names.xls"))

        cols = ["stn_code", "mrt_station_english", "mrt_line_english"]

        for col in cols:
            df[col] = df[col].str.strip()

        current_codes = MRTLineStation.objects.values_list("station_code", flat=True)
        df["stn_loaded"] = df["stn_code"].isin(current_codes)
        stations_df = df[~df["stn_loaded"]]

        current_mrt_lines = MRTLine.objects.values_list("name", flat=True)
        df["line_loaded"] = df["mrt_line_english"].isin(current_mrt_lines)
        lines_df = df[~df["line_loaded"]].drop_duplicates(subset=["mrt_line_english"])
        lines_df = lines_df.rename(columns={"mrt_line_english": "name"})
        lines_df["code"] = ""

        for idx, row in lines_df.iterrows():
            if options["use_defaults"]:
                lines_df.loc[idx, "code"] = DEFAULT_LINE_NAMES.get(row["name"])
            else:
                lines_df.loc[idx, "code"] = input(f"Enter line code for {row['name']}: ").strip()

        lines_to_create = lines_df[["name", "code"]].to_dict("records")
        lines_to_create = [MRTLine(**kwargs) for kwargs in lines_to_create]

        MRTLine.objects.bulk_create(lines_to_create)

        lines = dict(MRTLine.objects.values_list("name", "id"))

        with transaction.atomic():
            for idx, row in stations_df.iterrows():
                stn_name = row["mrt_station_english"]
                line_name = row["mrt_line_english"]
                stn_code = row["stn_code"]
                stn_obj, _created = Station.objects.get_or_create(name=stn_name)
                MRTLineStation.objects.create(
                    mrt_line_id=lines[line_name],
                    station=stn_obj,
                    station_code=stn_code
                )

        self.stdout.write(
            self.style.SUCCESS("MRT lines and stations are up-to-date.")
        )
