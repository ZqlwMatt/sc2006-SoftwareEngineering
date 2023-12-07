from DataAPIManager.db_API import dbAPI
import smtplib
import pandas as pd

class NotifManager():

    def __init__(self):
        self.db_obj = dbAPI()

        self.notif_email = 'IHateCongestion@gmail.com'
        self.pw= 'ywat fpeb yjkt zgnv'

        self.congestion_id={0:'Low', 1:'Moderately crowded', 2:'Very crowded', 999:'NA'}

    def send_email(self, receiver, body, server):

        subject = "MRT notifications"
        to = [receiver]

        email_text = "From:IHateCongestion.com \nTo:{0} \nSubject: {1} \n\n {2}".format(receiver,subject,body)
        print(email_text)

        server.sendmail(self.notif_email, to, email_text)
        return

    def get_list_of_people(self):
        return self.db_obj.getPeopleToNotify()


    def scheduler_loop(self):
        # Get list of ppl to notify
        noti_ppl_list = self.get_list_of_people()
        email_data = {}

        # Check for disruptions
        disrupted_stn = {}
        disruptions = self.db_obj.query_majordisruption_db()
        incidents = self.db_obj.count_reports()
        if disruptions:
            for i in disruptions:
                for x in i.affected_stations.all():
                    disrupted_stn[x.station_id] = i.description


        incident_stn_dict = {}
        if incidents:
            incident_stn = self.db_obj.query_announcements_db()
            df = pd.DataFrame(incident_stn)
            for stn in df['incident__station_id'].unique():
                content = df.query('incident__station_id=={0}'.format(stn))['content'].tolist()
                incident_stn_dict[stn] = ' \n'.join(["{0}) {1}".format(x+1,content[x]) for x in range(len(content))])


        # Get forecast/realtime data
        for person in noti_ppl_list:
            realtime = self.db_obj.query_congestion_db(person['stn_id']).congestion
            forecast = self.db_obj.query_congestionforecast_db(person['stn_id']).forecast
            # For first entry
            if person['id'] not in email_data.keys():

                email_data[person['id']] = {'email': person['email'], 'stn_info': [[person['stn'], realtime, forecast, person['stn_id'], person["rule"]]]}

            else:
                # Subsequent entries
                tmp = email_data[person['id']]
                tmp['stn_info'].append([person['stn'], realtime, forecast, person['stn_id'], person["rule"]])
                email_data[person['id']]['stn'] = tmp

        # Start email server
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(self.notif_email, self.pw)
        for person in email_data.keys():
            stn = []
            for data in email_data[person]['stn_info']:
                if data[4] == 'everyday':
                    stn.append("\nCurrent congestion at {0} is: {1}\nCongestion predicted in 20mins time at {0} : {2}".format(data[0], self.congestion_id[data[1]], self.congestion_id[data[2]]))

                if disruptions:
                    if data[3] in disrupted_stn.keys():
                        stn.append("\nALERT: {0}".format(disrupted_stn[data[3]]))
                if incidents:
                    if data[3] in incident_stn_dict.keys():
                        stn.append("\nIncident reported at {0}: \n{1}".format(data[0], incident_stn_dict[data[3]]))
            if not stn:
                continue

            email_body = "\n".join(stn)
            self.send_email(email_data[person]['email'], email_body, smtp_server)
        smtp_server.close()

if __name__ == "__main__":
    manager = NotifManager()
    manager.scheduler_loop()
